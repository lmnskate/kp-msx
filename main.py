import logging
from contextlib import asynccontextmanager

import uvicorn
from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config.settings import server
from models.Device import Device
from routers import content, proxy, registration, settings, static
from util import msx
from util import proxy as proxy_util

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
    app
):
    yield
    await proxy_util.close_session()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000
)
app.add_middleware(
    BrotliMiddleware,
    minimum_size=1000
)

app.include_router(static.router)
app.include_router(registration.router)
app.include_router(content.router)
app.include_router(settings.router)
app.include_router(proxy.router)
app.mount(
    '/icons',
    StaticFiles(directory='icons', html=False),
    name='icons'
)


UNAUTHORIZED_PATHS = frozenset([
    '/',
    '/subtitleShifter',
    '/paging.html',
    '/paging.js',
    '/html5x.html',
    '/html5x.js',
    '/hlsx.html',
    '/hlsx.js',
    '/hlsx-common.css',
    '/hlsx-subtitles.css',
    '/hlsx-roboto.css',
    '/msx/start.json',
    '/msx/proxy',
    '/msx/subtitle',
    '/msx/registration/code_image'
])


def cors_json_response(
    data
):
    response = JSONResponse(data)
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response


async def execute_guarded(
    request: Request,
    call_next,
    context: str
):
    try:
        return await call_next(request)
    except ExceptionGroup:
        logger.exception('Unhandled ExceptionGroup in %s', context)
        return cors_json_response(msx.handle_exception())
    except Exception:
        logger.exception('Unhandled error in %s', context)
        return cors_json_response(msx.handle_exception())


@app.middleware('http')
async def cache_icons(
    request: Request,
    call_next
):
    response = await execute_guarded(
        request,
        call_next,
        context='cache_icons'
    )

    if str(request.url.path).startswith('/icons/'):
        response.headers['Cache-Control'] = 'public, max-age=604800'

    return response


@app.middleware('http')
async def auth(
    request: Request,
    call_next
):
    if request.method == 'OPTIONS':
        return await call_next(request)

    path = str(request.url.path)
    device_id = request.query_params.get('id')

    if (
        device_id is None
        and path not in UNAUTHORIZED_PATHS
        and not path.startswith('/icons/')
    ):
        return cors_json_response({
            'response': {
                'status': 200,
                'data': {'action': 'warn:ID не может быть пустым'}
            }
        })

    if (
        device_id == '{ID}'
        and path not in UNAUTHORIZED_PATHS
        and not path.startswith('/icons/')
    ):
        return cors_json_response(msx.unsupported_version())

    request.state.device = None
    if device_id is not None:
        request.state.device = Device.by_id(device_id)
        if request.state.device is None:
            request.state.device = Device.create(device_id)

    device = request.state.device
    if device is not None and device.user_agent is None:
        ua = request.headers.get('user-agent')
        if ua is not None:
            device.update_user_agent(ua)

    try:
        return await execute_guarded(
            request,
            call_next,
            context='request'
        )
    finally:
        if device is not None and device.kp is not None:
            await device.kp.close_session()


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host=server.bind_host,
        port=server.bind_port or server.port,
        proxy_headers=server.proxy_headers,
        workers=server.workers
    )
