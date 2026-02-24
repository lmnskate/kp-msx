from fastapi import APIRouter
from starlette.requests import Request

from models.Category import Category
from models.Content import Content
from util import msx

router = APIRouter(prefix='/msx')


@router.get('/menu')
async def menu(request: Request):
    device = request.state.device

    if not device.registered():
        return msx.unregistered_menu()

    try:
        categories = await device.kp.get_content_categories()
    except Exception:
        return msx.handle_exception()

    if categories is None:
        device.delete()
        return msx.unregistered_menu()

    categories += Category.static_categories()
    for category in categories:
        if category.id in device.settings.menu_blacklist:
            category.blacklisted = True

    return msx.registered_menu(categories)


@router.get('/category')
async def category(request: Request):
    device = request.state.device

    page = int(request.query_params.get('page'))
    cat = request.query_params.get('category')
    extra = request.query_params.get('extra')
    genre = request.query_params.get('genre')
    sort = request.query_params.get('sort')

    result = await device.kp.get_content(
        category=cat, page=page, extra=extra, genre=genre, sort=sort,
    )
    return msx.content_list(
        result,
        category=cat,
        page=page,
        show_header=(extra is None and genre is None),
        small_posters=device.settings.small_posters,
    )


@router.get('/genres')
async def genres(request: Request):
    device = request.state.device
    cat = request.query_params.get('category')
    result = await device.kp.get_genres(category=cat)
    return msx.genre_folders(cat, result)


@router.get('/bookmarks')
async def bookmarks(request: Request):
    device = request.state.device
    result = await device.kp.get_bookmark_folders()
    if len(result) == 0:
        await device.kp.create_bookmark_folder()
        result = await device.kp.get_bookmark_folders()
    return msx.bookmark_folders(result)


@router.get('/tv')
async def tv(request: Request):
    device = request.state.device
    result = await device.kp.get_tv()
    return msx.tv_channels(
        result, alternative_player=device.settings.alternative_player,
    )


@router.get('/folder')
async def folder(request: Request):
    device = request.state.device
    page = int(request.query_params.get('page'))
    folder_id = request.query_params.get('folder')
    result = await device.kp.get_bookmark_folder(folder_id, page=page)
    return msx.content_list(
        result,
        page=page,
        small_posters=device.settings.small_posters,
    )


@router.get('/content')
async def content_detail(request: Request):
    device = request.state.device
    result = await device.kp.get_single_content(
        request.query_params.get('content_id'),
    )
    return result.to_msx_panel(
        proxy=device.settings.proxy,
        alternative_player=device.settings.alternative_player,
        small_poster=device.settings.small_posters,
    )


@router.get('/multivideo')
async def multivideo(request: Request):
    device = request.state.device
    result = await device.kp.get_single_content(
        request.query_params.get('content_id'),
    )
    return result.to_multivideo_msx_panel(
        proxy=device.settings.proxy,
        alternative_player=device.settings.alternative_player,
    )


@router.get('/content/bookmarks')
async def content_bookmarks(request: Request):
    device = request.state.device
    content_id = request.query_params.get('content_id')

    result = await device.kp.get_single_content(content_id)
    content_folders = await device.kp.get_content_folders(content_id)
    result.update_bookmarks(content_folders)

    folders = await device.kp.get_bookmark_folders()
    if len(folders) == 0:
        await device.kp.create_bookmark_folder()
        folders = await device.kp.get_bookmark_folders()

    return result.to_bookmarks_msx_panel(folders)


@router.get('/seasons')
async def seasons(request: Request):
    device = request.state.device
    result = await device.kp.get_single_content(
        request.query_params.get('content_id'),
    )
    return result.to_seasons_msx_panel()


@router.get('/episodes')
async def episodes(request: Request):
    device = request.state.device
    result = await device.kp.get_single_content(
        request.query_params.get('content_id'),
    )
    return result.to_episodes_msx_panel(
        int(request.query_params.get('season')),
        proxy=device.settings.proxy,
        alternative_player=device.settings.alternative_player,
    )


@router.get('/search')
async def search(request: Request):
    device = request.state.device
    query = request.query_params.get('q')
    result = await device.kp.search(query)
    return msx.content_list(
        result,
        decompress=False,
        small_posters=device.settings.small_posters,
    )


@router.get('/history')
async def history(request: Request):
    device = request.state.device
    page = int(request.query_params.get('page'))
    result = await device.kp.get_history(page=page)
    return msx.content_list(
        result,
        page=page,
        small_posters=device.settings.small_posters,
    )


@router.get('/watching')
async def watching(request: Request):
    device = request.state.device
    result = await device.kp.get_watching(subscribed=1)
    return msx.content_list(
        result,
        small_posters=device.settings.small_posters,
    )


@router.get('/collections')
async def collections(request: Request):
    device = request.state.device
    page = request.query_params.get('page')
    result = await device.kp.get_collections(page=page)
    return msx.collections(
        result, small_posters=device.settings.small_posters,
    )


@router.get('/collection')
async def single_collection(request: Request):
    device = request.state.device
    collection_id = request.query_params.get('collection_id')
    result = await device.kp.get_single_collection(collection_id)
    return msx.content_list(
        result,
        small_posters=device.settings.small_posters,
    )


@router.post('/play')
async def play(request: Request):
    device = request.state.device
    content_id = request.query_params.get('content_id')
    season = request.query_params.get('season')
    episode = request.query_params.get('episode')

    result = await device.kp.get_single_content(content_id)

    if season is not None and episode is not None:
        for _season in result.seasons:
            if _season.n != int(season):
                continue
            for _episode in _season.episodes:
                if _episode.n == int(episode):
                    if not _episode.watched:
                        await device.kp.toggle_watched(
                            content_id, season, episode,
                        )
                    break
            break
    else:
        if not result.watched:
            await device.kp.toggle_watched(content_id)

    return msx.empty_response()


@router.post('/toggle_subscription')
async def toggle_subscription(request: Request):
    device = request.state.device
    content_id = request.query_params.get('content_id')
    await device.kp.toggle_subscription(content_id)
    result = await device.kp.get_single_content(content_id)
    return msx.update_panel(
        Content.SUBSCRIPTION_BUTTON_ID, result.to_subscription_button(),
    )


@router.post('/toggle_bookmark')
async def toggle_bookmark(request: Request):
    device = request.state.device
    content_id = request.query_params.get('content_id')
    folder_id = int(request.query_params.get('folder_id'))

    await device.kp.toggle_bookmark(content_id, folder_id)
    result = await device.kp.get_single_content(content_id)
    content_folders = await device.kp.get_content_folders(content_id)
    result.update_bookmarks(content_folders)

    return msx.update_panel(str(folder_id), result.to_bookmark_stamp(folder_id))
