from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import FileResponse

from util import msx

router = APIRouter()


@router.get('/')
async def index(request: Request):
    return FileResponse('pages/index.html')


@router.get('/subtitleShifter')
async def subtitle_shifter(request: Request):
    return FileResponse('pages/subtitle_shifter.html')


@router.get('/paging.html')
async def paging_html(request: Request):
    return FileResponse('pages/paging.html')


@router.get('/paging.js')
async def paging_js(request: Request):
    return FileResponse('pages/paging.js')


@router.get('/msx/start.json')
async def start(request: Request):
    return msx.start()
