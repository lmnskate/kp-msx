from fastapi import APIRouter
from starlette.requests import Request

from config.globals import SERVER_ID
from models.Category import Category
from models.Device import KP_TOGGLES, LOCAL_TOGGLES
from util import msx

router = APIRouter(
    prefix='/msx/settings'
)


@router.get('/screen')
async def settings_screen(
    request: Request
):
    return msx.settings_screen(screen=True)


@router.get('')
async def settings(
    request: Request
):
    return msx.settings_menu(request.state.device.settings)


@router.get('/menu_entries')
async def menu_entries(
    request: Request
):
    device = request.state.device

    categories = await device.kp.get_content_categories()
    categories += Category.static_categories()
    for category in categories:
        if category.id in device.settings.menu_blacklist:
            category.blacklisted = True

    return msx.menu_entries_settings_panel(categories)


@router.post('/toggle/{setting}')
async def toggle_setting(
    request: Request,
    setting: str
):
    device = request.state.device

    if setting in KP_TOGGLES or setting in LOCAL_TOGGLES:
        attr = await device.toggle(setting)
        return msx.update_panel(
            setting,
            msx.stamp(getattr(device.settings, attr))
        )

    if setting == SERVER_ID:
        new_label = await device.toggle_server()
        return msx.update_panel(SERVER_ID, msx.label(new_label))

    return msx.empty_response()


@router.post('/toggle_menu_entry/{menu_entry}')
async def toggle_menu_entry(
    request: Request,
    menu_entry: str
):
    current_state = request.state.device.toggle_menu_entry(menu_entry)
    return msx.update_panel(menu_entry, msx.stamp(current_state))


@router.post('/reset_menu')
async def reset_menu(
    request: Request
):
    request.state.device.reset_menu()
    return msx.restart()
