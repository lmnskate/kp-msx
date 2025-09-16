import traceback

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse, FileResponse

import config
from models.Content import Content
from models.Device import Device
from models.KinoPub import KinoPub
from models.MSX import MSX


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENDPOINT = '/msx'
UNAUTHORIZED = [
    '/',
    '/subtitleShifter',
    ENDPOINT + '/start.json'
]


@app.middleware('http')
async def auth(request: Request, call_next):
    if request.method == 'OPTIONS':
        return await call_next(request)
    device_id = request.query_params.get('id')

    if device_id is None and str(request.url.path) not in UNAUTHORIZED:
        result = JSONResponse({
            'response': {
                'status': 200,
                'data': {'action': 'warn:ID не может быть пустым'}
            }
        })
        result.headers['Access-Control-Allow-Credentials'] = 'true'
        result.headers['Access-Control-Allow-Origin'] = '*'
        return result

    if device_id == '{ID}' and str(request.url.path) not in UNAUTHORIZED:
        result = JSONResponse(MSX.unsupported_version())
        result.headers['Access-Control-Allow-Credentials'] = 'true'
        result.headers['Access-Control-Allow-Origin'] = '*'
        return result

    request.state.device = Device.by_id(device_id)
    if request.state.device is None and device_id is not None:
        request.state.device = Device.create(device_id)
    try:
        result = await call_next(request)
    except Exception as e:
        result = JSONResponse(MSX.handle_exception())
        result.headers['Access-Control-Allow-Credentials'] = 'true'
        result.headers['Access-Control-Allow-Origin'] = '*'
        traceback.print_exc()
    return result


@app.get('/')
async def index(request: Request):
    return FileResponse('pages/index.html')

@app.get('/subtitleShifter')
async def subtitle_editor(request: Request):
    return FileResponse('pages/subtitle_shifter.html')


@app.get(ENDPOINT + '/start.json')
async def start(request: Request):
    return MSX.start()


@app.get(ENDPOINT + '/menu')
async def menu(request: Request):
    if not request.state.device.registered():
        return MSX.unregistered_menu()

    categories = await request.state.device.kp.get_content_categories()
    if categories is None:
        request.state.device.delete()
        return MSX.unregistered_menu()
    return MSX.registered_menu(categories)


@app.get(ENDPOINT + '/registration')
async def registration(request: Request):
    if request.state.device.registered():
        return MSX.already_registered()
    else:
        user_code, device_code = await KinoPub.get_codes()
        request.state.device.update_code(device_code)
        return MSX.registration(user_code)


@app.post(ENDPOINT + '/check_registration')
async def check_registration(request: Request):
    result = await KinoPub.check_registration(request.state.device.code)
    if result is None:
        return MSX.code_not_entered()
    request.state.device.update_tokens(result['access_token'], result['refresh_token'])
    await request.state.device.notify()
    return MSX.restart()


@app.get(ENDPOINT + '/category')
async def category(request: Request):
    offset = request.query_params.get('offset') or 0
    page = int(offset) // 20 + 1
    cat = request.query_params.get('category')
    extra = request.query_params.get('extra')
    genre = request.query_params.get('genre')
    result = await request.state.device.kp.get_content(cat, page=page, extra=extra, genre=genre)
    result = MSX.content(result, cat, page, extra=(extra or genre))
    return result


@app.get(ENDPOINT + '/genres')
async def category(request: Request):
    cat = request.query_params.get('category')
    result = await request.state.device.kp.get_genres(category=cat)
    result = MSX.genre_folders(cat, result)
    return result


@app.get(ENDPOINT + '/bookmarks')
async def bookmarks(request: Request):
    result = await request.state.device.kp.get_bookmark_folders()

    result = MSX.bookmark_folders(result)
    return result


@app.get(ENDPOINT + '/tv')
async def bookmarks(request: Request):
    result = await request.state.device.kp.get_tv()

    result = MSX.tv_channels(result)
    return result


@app.get(ENDPOINT + '/folder')
async def folder(request: Request):
    offset = request.query_params.get('offset') or 0
    page = int(offset) // 20 + 1
    f = request.query_params.get('folder')
    result = await request.state.device.kp.get_bookmark_folder(f, page=page)
    result = MSX.content(result, "folder", page, extra="wtf")
    return result


@app.get(ENDPOINT + '/content')
async def content(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    return result.to_msx_panel()


@app.get(ENDPOINT + '/multivideo')
async def content(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    return result.to_multivideo_msx_panel()


@app.get(ENDPOINT + '/content/bookmarks')
async def content_bookmarks(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    folders = await request.state.device.kp.get_bookmark_folders()
    return result.to_bookmarks_msx_panel(folders)


@app.get(ENDPOINT + '/seasons')
async def seasons(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    panel = result.to_seasons_msx_panel()
    return panel


@app.get(ENDPOINT + '/episodes')
async def episodes(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    return result.to_episodes_msx_panel(int(request.query_params.get('season')))


@app.get(ENDPOINT + '/search')
async def search(request: Request):
    result = await request.state.device.kp.search(request.query_params.get('q'))
    result = MSX.content(result, "search", 1, extra=request.query_params.get('q'), decompress=False)
    return result


@app.get(ENDPOINT + '/history')
async def history(request: Request):
    offset = request.query_params.get('offset') or 0
    page = int(offset) // 20 + 1
    result = await request.state.device.kp.get_history(page=page)
    result = MSX.content(result, "history", page, extra="wtf")
    return result


@app.get(ENDPOINT + '/watching')
async def watching(request: Request):
    result = await request.state.device.kp.get_watching(subscribed=1)
    result = MSX.content(result, "watching", 0, extra='wtf')
    return result


@app.post(ENDPOINT + '/play')
async def play(request: Request):
    content_id = request.query_params.get('content_id')
    season = request.query_params.get('season')
    episode = request.query_params.get('episode')
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))

    if season is not None and episode is not None:
        for _season in result.seasons:
            if _season.n != int(season):
                continue
            for _episode in _season.episodes:
                if _episode.n == int(episode):
                    if not _episode.watched:
                        await request.state.device.kp.toggle_watched(content_id, season, episode)
                    break
            break
    else:
        if not result.watched:
            await request.state.device.kp.toggle_watched(content_id)

    return MSX.empty_response()


@app.post(ENDPOINT + '/toggle_subscription')
async def toggle_subscription(request: Request):
    content_id = request.query_params.get('content_id')
    await request.state.device.kp.toggle_subscription(content_id)
    result = await request.state.device.kp.get_single_content(content_id)
    return MSX.update_panel(Content.SUBSCRIPTION_BUTTON_ID, result.to_subscription_button())


@app.post(ENDPOINT + '/toggle_bookmark')
async def toggle_bookmark(request: Request):
    content_id = request.query_params.get('content_id')
    folder_id = int(request.query_params.get('folder_id'))
    await request.state.device.kp.toggle_bookmark(content_id, folder_id)
    result = await request.state.device.kp.get_single_content(content_id)
    upd = result.to_bookmark_stamp(folder_id)
    return MSX.update_panel(str(folder_id), upd)


@app.get(ENDPOINT + '/error')
async def error_page(request: Request):
    return MSX.handle_exception(error_page=True)


@app.get(ENDPOINT + '/too_old')
async def too_old(request: Request):
    return MSX.unsupported_version()


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(config.PORT))

