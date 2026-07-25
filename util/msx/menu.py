from util.msx.core import (POSTER_TEMPLATE, build_list, format_action, icon,
                           sad_screen)
from util.msx.player import player_action_btn
from util.msx.settings import settings_screen


def start():
    return {
        'name': 'Kinopub',
        'version': '2.1.0',
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


def registered_menu(categories: list):
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
        'options': settings_screen(),
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

    resp = build_list(
        '0,0,2,4',
        [entry.to_msx(device_settings=device_settings) for entry in entries],
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


def collections(entries, *, device_settings=None):
    return build_list(
        '0,0,3,6',
        [entry.to_msx(device_settings=device_settings) for entry in entries],
        template_extra={**POSTER_TEMPLATE, 'imageOverlay': 3},
        preload='next'
    )


def bookmark_folders(result):
    return build_list(
        '0,0,4,1',
        [i.to_msx() for i in result],
        headline='Закладки'
    )


def genre_folders(category, result):
    return build_list(
        '0,0,4,1',
        [i.to_msx(category) for i in result],
        headline='Жанры'
    )


def country_list(category, result):
    return build_list(
        '0,0,4,1',
        [i.to_msx(category) for i in result],
        headline='Страны'
    )


def tv_channels(channels, alternative_player: bool = False):
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
        ]
    }
