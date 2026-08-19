import asyncio
import logging

from fastapi import APIRouter
from starlette.requests import Request

from config.globals import SUBSCRIPTION_BUTTON_ID
from models.Content import Content
from util import msx
from util.proxy import extract_audio_tracks

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/msx'
)


def _int_param(
    request: Request,
    name: str,
    default: int = 0
) -> int:
    value = request.query_params.get(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        logger.warning(
            'Invalid %s query parameter: %r',
            name,
            value
        )

        return default


def _page(
    request: Request
) -> int:
    return _int_param(request, 'page', 1)


async def _get_content(
    device,
    request: Request
):
    return await device.kp.get_single_content(
        request.query_params.get('content_id')
    )


async def _ensure_bookmark_folders(
    kp
):
    folders = await kp.get_bookmark_folders()
    if len(folders) == 0:
        await kp.create_bookmark_folder()
        folders = await kp.get_bookmark_folders()

    return folders


@router.get('/menu')
async def menu(
    request: Request
):
    device = request.state.device

    if not device.registered():
        return msx.unregistered_menu()

    categories = await msx.build_categories(device)

    return msx.registered_menu(categories)


@router.get('/category')
async def category(
    request: Request
):
    device = request.state.device

    page = _page(request)
    cat = request.query_params.get('category')
    extra = request.query_params.get('extra')
    genre = request.query_params.get('genre')
    country = request.query_params.get('country')
    sort = request.query_params.get('sort')

    result = await device.kp.get_content(
        category=cat,
        page=page,
        extra=extra,
        genre=genre,
        country=country,
        sort=sort
    )

    return msx.content_list(
        result,
        category=cat,
        page=page,
        show_header=(extra is None and genre is None and country is None),
        device_settings=device.settings
    )


@router.get('/genres')
async def genres(
    request: Request
):
    device = request.state.device
    cat = request.query_params.get('category')
    result = await device.kp.get_genres(category=cat)

    return msx.genre_folders(
        cat,
        result
    )


@router.get('/bookmarks')
async def bookmarks(
    request: Request
):
    device = request.state.device
    result = await _ensure_bookmark_folders(device.kp)

    return msx.bookmark_folders(result)


@router.get('/tv')
async def tv(
    request: Request
):
    device = request.state.device
    result = await device.kp.get_tv()

    return msx.tv_channels(
        result,
        alternative_player=device.settings.alternative_player
    )


@router.get('/folder')
async def folder(
    request: Request
):
    device = request.state.device
    page = _page(request)
    folder_id = request.query_params.get('folder')
    result = await device.kp.get_bookmark_folder(
        folder_id,
        page=page
    )

    return msx.content_list(
        result,
        page=page,
        device_settings=device.settings
    )


@router.get('/content')
async def content_detail(
    request: Request
):
    device = request.state.device
    result = await _get_content(device, request)
    if result is None:
        return msx.handle_exception()

    return result.to_msx_panel(
        proxy=device.settings.proxy,
        alternative_player=device.settings.alternative_player,
        device_settings=device.settings
    )


@router.get('/multivideo')
async def multivideo(
    request: Request
):
    device = request.state.device
    result = await _get_content(device, request)
    if result is None:
        return msx.handle_exception()

    audio_tracks_by_index = {}
    if result.videos:
        tasks = [
            (index, extract_audio_tracks(video.video_url))
            for index, video in enumerate(result.videos)
            if video.video_url
        ]
        if tasks:
            results = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )
            for (index, _), tracks in zip(tasks, results):
                if isinstance(tracks, list) and tracks:
                    audio_tracks_by_index[index] = tracks

    return result.to_multivideo_msx_panel(
        proxy=device.settings.proxy,
        alternative_player=device.settings.alternative_player,
        device_settings=device.settings,
        audio_tracks_by_index=audio_tracks_by_index
    )


@router.get('/content/bookmarks')
async def content_bookmarks(
    request: Request
):
    device = request.state.device
    content_id = request.query_params.get('content_id')

    content_folders = await device.kp.get_content_folders(content_id)
    result = Content({'id': content_id})
    result.update_bookmarks(content_folders)

    folders = await _ensure_bookmark_folders(device.kp)

    return result.to_bookmarks_msx_panel(folders)


@router.get('/seasons')
async def seasons(
    request: Request
):
    device = request.state.device
    result = await _get_content(device, request)
    if result is None:
        return msx.handle_exception()

    return result.to_seasons_msx_panel(
        device_settings=device.settings
    )


@router.get('/episodes')
async def episodes(
    request: Request
):
    device = request.state.device
    result = await _get_content(device, request)
    if result is None:
        return msx.handle_exception()

    return result.to_episodes_msx_panel(
        _int_param(request, 'season', 1),
        proxy=device.settings.proxy,
        alternative_player=device.settings.alternative_player,
        device_settings=device.settings
    )


@router.get('/search')
async def search(
    request: Request
):
    device = request.state.device
    query = request.query_params.get('q')
    result = await device.kp.search(query)

    return msx.content_list(
        result,
        decompress=False,
        device_settings=device.settings
    )


@router.get('/history')
async def history(
    request: Request
):
    device = request.state.device
    page = _page(request)
    result = await device.kp.get_history(page=page)

    return msx.content_list(
        result,
        page=page,
        device_settings=device.settings
    )


@router.get('/watching')
async def watching(
    request: Request
):
    device = request.state.device
    result = await device.kp.get_watching(subscribed=1)

    return msx.content_list(
        result,
        device_settings=device.settings
    )


@router.get('/collections')
async def collections(
    request: Request
):
    device = request.state.device
    page = _page(request)
    result = await device.kp.get_collections(page=page)

    return msx.collections(
        result,
        page=page,
        device_settings=device.settings
    )


@router.get('/collection')
async def single_collection(
    request: Request
):
    device = request.state.device
    collection_id = request.query_params.get('collection_id')
    result = await device.kp.get_single_collection(collection_id)

    return msx.content_list(
        result,
        device_settings=device.settings
    )


@router.get('/similar')
async def similar(
    request: Request
):
    device = request.state.device
    result = await device.kp.get_similar(
        request.query_params.get('content_id')
    )

    return msx.content_list(
        result,
        device_settings=device.settings
    )


@router.get('/unfinished')
async def unfinished(
    request: Request
):
    device = request.state.device
    movies = await device.kp.get_watching_movies()
    serials = await device.kp.get_watching(subscribed=0)

    return msx.content_list(
        movies + serials,
        device_settings=device.settings
    )


@router.get('/countries')
async def countries(
    request: Request
):
    device = request.state.device
    result = await device.kp.get_countries()

    return msx.country_list(
        request.query_params.get('category'),
        result
    )


@router.post('/clear_history')
async def clear_history(
    request: Request
):
    device = request.state.device
    await device.kp.clear_history_item(
        request.query_params.get('content_id')
    )

    return msx.empty_response()


@router.post('/play')
async def play(
    request: Request
):
    device = request.state.device
    content_id = request.query_params.get('content_id')
    season = request.query_params.get('season')
    episode = request.query_params.get('episode')

    result = await _get_content(device, request)
    if result is None:
        return msx.empty_response()

    season = _int_param(request, 'season', 0)
    episode = _int_param(request, 'episode', 0)

    if season > 0 and episode > 0:
        for s in result.seasons or []:
            if s.n != season:
                continue
            for ep in s.episodes:
                if ep.n == episode:
                    if not ep.watched:
                        await device.kp.toggle_watched(
                            content_id,
                            str(season),
                            str(episode)
                        )
                    break
            break
    else:
        if not result.watched:
            await device.kp.toggle_watched(content_id)

    return msx.empty_response()


@router.post('/toggle_subscription')
async def toggle_subscription(
    request: Request
):
    device = request.state.device
    content_id = request.query_params.get('content_id')
    await device.kp.toggle_subscription(content_id)
    result = await _get_content(device, request)
    if result is None:
        return msx.empty_response()

    return msx.update_panel(
        SUBSCRIPTION_BUTTON_ID,
        result.to_subscription_button()
    )


@router.post('/toggle_bookmark')
async def toggle_bookmark(
    request: Request
):
    device = request.state.device
    content_id = request.query_params.get('content_id')
    folder_id = _int_param(request, 'folder_id', 0)

    await device.kp.toggle_bookmark(
        content_id,
        folder_id
    )
    content_folders = await device.kp.get_content_folders(content_id)
    result = Content({'id': content_id})
    result.update_bookmarks(content_folders)

    return msx.update_panel(
        str(folder_id),
        result.to_bookmark_stamp(folder_id)
    )
