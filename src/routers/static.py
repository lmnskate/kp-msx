from pathlib import Path

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import FileResponse

from util import msx

PAGES_DIR = Path(__file__).resolve().parent.parent / 'pages'

router = APIRouter()


@router.get('/')
async def index(
    request: Request
):
    return FileResponse(PAGES_DIR / 'index.html')


@router.get('/subtitleShifter')
async def subtitle_shifter(
    request: Request
):
    return FileResponse(PAGES_DIR / 'subtitle_shifter.html')


@router.get('/paging.html')
async def paging_html(
    request: Request
):
    return FileResponse(PAGES_DIR / 'paging.html')


@router.get('/paging.js')
async def paging_js(
    request: Request
):
    return FileResponse(PAGES_DIR / 'paging.js')


@router.get('/html5x.html')
async def html5x_html(
    request: Request
):
    return FileResponse(PAGES_DIR / 'html5x.html')


@router.get('/html5x.js')
async def html5x_js(
    request: Request
):
    return FileResponse(PAGES_DIR / 'html5x.js')


@router.get('/hlsx.html')
async def hlsx_html(
    request: Request
):
    return FileResponse(PAGES_DIR / 'hlsx.html')


@router.get('/hlsx.js')
async def hlsx_js(
    request: Request
):
    return FileResponse(PAGES_DIR / 'hlsx.js')


@router.get('/hlsx-common.css')
async def hlsx_common_css(
    request: Request
):
    return FileResponse(PAGES_DIR / 'hlsx-common.css')


@router.get('/hlsx-subtitles.css')
async def hlsx_subtitles_css(
    request: Request
):
    return FileResponse(PAGES_DIR / 'hlsx-subtitles.css')


@router.get('/hlsx-roboto.css')
async def hlsx_roboto_css(
    request: Request
):
    return FileResponse(PAGES_DIR / 'hlsx-roboto.css')


@router.get('/msx/start.json')
async def start(
    request: Request
):
    return msx.start()
