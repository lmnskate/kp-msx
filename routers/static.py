from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import FileResponse

from util import msx

router = APIRouter()


@router.get('/')
async def index(
    request: Request
):
    return FileResponse('pages/index.html')


@router.get('/subtitleShifter')
async def subtitle_shifter(
    request: Request
):
    return FileResponse('pages/subtitle_shifter.html')


@router.get('/paging.html')
async def paging_html(
    request: Request
):
    return FileResponse('pages/paging.html')


@router.get('/paging.js')
async def paging_js(
    request: Request
):
    return FileResponse('pages/paging.js')


@router.get('/html5x.html')
async def html5x_html(
    request: Request
):
    return FileResponse('pages/html5x.html')


@router.get('/html5x.js')
async def html5x_js(
    request: Request
):
    return FileResponse('pages/html5x.js')


@router.get('/hlsx.html')
async def hlsx_html(
    request: Request
):
    return FileResponse('pages/hlsx.html')


@router.get('/hlsx.js')
async def hlsx_js(
    request: Request
):
    return FileResponse('pages/hlsx.js')


@router.get('/hlsx-common.css')
async def hlsx_common_css(
    request: Request
):
    return FileResponse('pages/hlsx-common.css')


@router.get('/hlsx-subtitles.css')
async def hlsx_subtitles_css(
    request: Request
):
    return FileResponse('pages/hlsx-subtitles.css')


@router.get('/hlsx-roboto.css')
async def hlsx_roboto_css(
    request: Request
):
    return FileResponse('pages/hlsx-roboto.css')


@router.get('/msx/start.json')
async def start(
    request: Request
):
    return msx.start()
