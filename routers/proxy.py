from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response

from util import msx, proxy

router = APIRouter(prefix='/msx')


@router.get('/proxy')
async def proxy_request(request: Request):
    url = request.query_params.get('url')
    try:
        proxy.check_url(url)
        code, content_type, contents = await proxy.get(url)
    except Exception:
        return Response(status_code=403)
    return Response(contents, code, media_type=content_type)


@router.get('/error')
async def error_page(request: Request):
    return msx.handle_exception(error_page=True)


@router.get('/too_old')
async def too_old(request: Request):
    return msx.unsupported_version()
