from util.msx.core import (POSTER_TEMPLATE, build_list, empty_item,
                           format_action, icon, sad_screen)
from util.msx.player import player_action_btn
from util.msx.settings import settings_screen


async def build_categories(
    device
):
    # Local import: models.Category imports util.msx, a top-level import
    # here would create a circular import.
    from models.Category import Category

    categories = await device.kp.get_content_categories()
    categories += Category.static_categories()
    for category in categories:
        if category.id in device.settings.menu_blacklist:
            category.blacklisted = True

    return categories


def start():
    return {
        'name': 'Kinopub',
        'version': '2.5.0',
        'parameter': format_action('/msx/menu', module='menu'),
        'welcome': 'none',
        'launcher': {
            'parameter': format_action('/msx/menu', module='menu'),
            'image': icon('logo'),
            'color': 'none'
        }
    }


def unregistered_menu():
    return {
        'reuse': False,
        'cache': False,
        'restore': False,
        'headline': 'Kinopub',
        'menu': [
            {
                'image': icon('key'),
                'label': 'Регистрация',
                'data': format_action('/msx/registration')
            }
        ]
    }


def registered_menu(
    categories: list,
    device_settings=None
):
    menu = [
        category.to_msx()
        for category in (categories or [])
        if not category.blacklisted
    ]

    if not menu:
        menu = [sad_screen()]

    return {
        'reuse': False,
        'cache': False,
        'restore': False,
        'refocus': 1,
        'headline': 'Kinopub',
        'options': settings_screen(device_settings=device_settings),
        'menu': menu
    }


def content_list(
    entries,
    *,
    category=None,
    page=1,
    show_header=False,
    decompress=None,
    device_settings=None
):
    extra = {**POSTER_TEMPLATE, 'imageOverlay': 2}
    if decompress is not None:
        extra['decompress'] = decompress

    items = [
        entry.to_msx(device_settings=device_settings)
        for entry in entries
    ]
    if not items and page == 1:
        items = [empty_item()]

    resp = build_list(
        '0,0,2,4',
        items,
        template_extra=extra,
        preload='next'
    )

    if show_header and page == 1:
        from models.CategoryExtra import CategoryExtra

        resp['header'] = {
            'items': [
                i.to_msx(category) for i in CategoryExtra.static_extras()
            ]
        }

    return resp


def collections(
    entries,
    *,
    page=1,
    device_settings=None
):
    items = [
        entry.to_msx(device_settings=device_settings)
        for entry in entries
    ]
    if not items and page == 1:
        items = [empty_item()]

    return build_list(
        '0,0,3,6',
        items,
        template_extra={**POSTER_TEMPLATE, 'imageOverlay': 3},
        preload='next'
    )


def bookmark_folders(
    result
):
    return build_list(
        '0,0,4,1',
        [i.to_msx() for i in result] or [empty_item()],
        headline='Закладки'
    )


def genre_folders(
    category,
    result
):
    return build_list(
        '0,0,4,1',
        [i.to_msx(category) for i in result] or [empty_item()],
        headline='Жанры'
    )


def country_list(
    category,
    result
):
    return build_list(
        '0,0,4,1',
        [i.to_msx(category) for i in result] or [empty_item()],
        headline='Страны'
    )


def tv_channels(
    channels,
    alternative_player: bool = False
):
    return {
        'type': 'list',
        'header': {
            'items': [
                {
                    'type': 'default',
                    'layout': '0,0,12,1',
                    'color': 'msx-glass',
                    'headline': 'Спортивные каналы предоставляются в качестве бонуса и работают «как есть»',
                    'titleFooter': 'Для просмотра полноценного онлайн-ТВ с архивом рекомендуется использовать другие сервисы',
                    'action': '[]'
                }
            ]
        },
        'template': {
            'type': 'separate',
            'layout': '0,0,2,3',
            'color': 'msx-glass',
            'imageFiller': 'height-center',
            'title': 'Title',
            'properties': {
                'control:type': 'extended',
                'button:content:enable': 'false',
                'button:restart:icon': 'settings',
                'button:restart:action': player_action_btn(),
                'progress:display': 'false'
            }
        },
        'items': [
            channel.to_msx(alternative_player=alternative_player)
            for channel in channels
        ] or [empty_item()]
    }
