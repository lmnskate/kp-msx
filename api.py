import traceback

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import JSONResponse

import config
from models.Device import Device
from routers import content, proxy, registration, settings, static
from util import msx

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(static.router)
app.include_router(registration.router)
app.include_router(content.router)
app.include_router(settings.router)
app.include_router(proxy.router)
app.mount(
    '/icons',
    StaticFiles(directory='icons', html=False),
    name='icons',
)


@app.middleware('http')
async def cache_icons(request: Request, call_next):
    response = await call_next(request)
    if str(request.url.path).startswith('/icons/'):
        response.headers['Cache-Control'] = 'public, max-age=604800'
    return response

UNAUTHORIZED_PATHS = frozenset([
    '/',
    '/subtitleShifter',
    '/paging.html',
    '/paging.js',
    '/msx/start.json',
    '/msx/proxy',
])


def _cors_json_response(data):
    response = JSONResponse(data)
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.middleware('http')
async def auth(request: Request, call_next):
    if request.method == 'OPTIONS':
        return await call_next(request)

    path = str(request.url.path)
    device_id = request.query_params.get('id')

    if device_id is None and path not in UNAUTHORIZED_PATHS and not path.startswith('/icons/'):
        return _cors_json_response({
            'response': {
                'status': 200,
                'data': {'action': 'warn:ID не может быть пустым'},
            },
        })

    if device_id == '{ID}' and path not in UNAUTHORIZED_PATHS and not path.startswith('/icons/'):
        return _cors_json_response(msx.unsupported_version())

    request.state.device = Device.by_id(device_id)
    if request.state.device is None and device_id is not None:
        request.state.device = Device.create(device_id)

    device = request.state.device
    if device is not None and device.user_agent is None:
        ua = request.headers.get('user-agent')
        if ua is not None:
            device.update_user_agent(ua)

    try:
        return await call_next(request)
    except Exception:
        traceback.print_exc()
        return _cors_json_response(msx.handle_exception())


if __name__ == '__main__':
    uvicorn.run(
        app=app,
        host='0.0.0.0',
        port=int(config.PORT),
    )
