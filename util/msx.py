from urllib.parse import urlencode

from config.globals import ALTERNATIVE_PLAYER_URL, LENNY, PLAYER_URL, SAD_LENNY
from config.settings import server
from util.proxy import make_proxy_url

POSTER_TEMPLATE = {
    'imageFiller': 'height-center',
    'title': 'Title'
}

DEFAULT_PLAY_BUTTON_PROPS = {
    'control:type': 'extended',
    'button:content:icon': 'audiotrack',
    'button:content:action': 'panel:request:player:audiotrack',
    'button:restart:icon': 'settings',
    'button:restart:action': 'panel:request:player:options',
    'button:speed:icon': 'subtitles',
    'button:speed:action': 'panel:request:player:subtitle'
}


def icon(name):
    return f'{server.base_url}/icons/{name}.svg'


def format_action(
    path: str,
    params: dict = None,
    interaction: str = None,
    options: str = None,
    module: str = None
):
    params = {**(params or {}), 'id': '{ID}'}

    if path.startswith('/'):
        data = f'{server.base_url}{path}'
    else:
        data = path

    data = f'{data}?{urlencode(params, safe="{}")}'

    if interaction:
        if interaction.startswith('/'):
            interaction = f'{server.base_url}{interaction}'

        data = f'request:interaction:{data}'
        if options:
            data = f'{data}|{options}'
        data = f'{data}@{interaction}'

    if module:
        data = f'{module}:{data}'

    return data


def start():
    return {
        'name': 'Kinopub',
        'version': '2.0.0',
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


def sad_screen():
    return {
        'type': 'default',
        'label': SAD_LENNY,
        'data': {
            'type': 'pages',
            'headline': SAD_LENNY,
            'pages': [
                {
                    'items': [
                        {
                            'type': 'space',
                            'layout': '0,0,8,3',
                            'color': 'msx-glass',
                            'alignment': 'center',
                            'headline': 'Вот так вот',
                            'text': 'Вы выключили все разделы меню, поэтому теперь здесь ничего нет.'
                        },
                        {
                            'type': 'button',
                            'layout': '2,3,4,1',
                            'image': icon('refresh'),
                            'label': 'Вернуть назад',
                            'action': format_action(
                                '/msx/settings/reset_menu', module='execute'
                            )
                        }
                    ]
                }
            ]
        }
    }


def already_registered():
    return {
        'type': 'pages',
        'headline': 'Регистрация',
        'pages': [
            {
                'items': [
                    {
                        'type': 'space',
                        'layout': '0,0,12,5',
                        'color': 'msx-glass',
                        'alignment': 'center',
                        'headline': 'Уже зарегистрирован',
                        'text': 'Это устройство уже привязано к аккаунту Kinopub'
                    },
                    {
                        'type': 'button',
                        'layout': '0,5,12,1',
                        'enumerate': False,
                        'label': 'Перезапустить приложение',
                        'action': 'reload'
                    }
                ]
            }
        ]
    }


def code_image(user_code):
    return f'{server.base_url}/msx/registration/code_image?{urlencode({"code": user_code})}'


def registration(user_code):
    return {
        'type': 'pages',
        'headline': 'Регистрация',
        'pages': [
            {
                'items': [
                    {
                        'type': 'space',
                        'layout': '0,0,12,5',
                        'color': 'msx-glass',
                        'image': code_image(user_code),
                        'imageFiller': 'fit',
                        'imageOverlay': 0
                    },
                    {
                        'type': 'button',
                        'layout': '0,5,12,1',
                        'enumerate': False,
                        'label': 'Проверить код',
                        'action': format_action(
                            '/msx/check_registration', module='execute'
                        )
                    }
                ]
            }
        ]
    }


def code_not_entered():
    return {
        'response': {
            'status': 200,
            'data': {
                'action': 'warn:Код не введён. Если прошло больше 5 минут, перезапустите приложение для получения нового кода.'
            }
        }
    }


def restart():
    return {'response': {'status': 200, 'data': {'action': 'reload'}}}


def build_list(layout, items, *, template_extra=None, **kwargs):
    template = {
        'type': 'separate',
        'layout': layout,
        'color': 'msx-glass',
    }
    if template_extra:
        template.update(template_extra)
    return {
        'type': 'list',
        'template': template,
        'items': items,
        **kwargs
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


def update_panel(content_id, value):
    return {
        'response': {
            'status': 200,
            'data': {'action': f'update:panel:{content_id}', 'data': value}
        }
    }


def empty_response():
    return {'response': {'status': 200, 'data': {'action': '[]'}}}


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


def handle_exception(error_page=False):
    msg = {
        'type': 'space',
        'layout': '0,0,8,2',
        'color': 'msx-glass',
        'alignment': 'center',
        'headline': 'Произошла ошибка загрузки',
        'text': 'Скорее всего, кинопаб сейчас недоступен - проверьте статус на kino.pub и ожидайте ремонта'
    }
    restart_app_btn = {
        'type': 'button',
        'layout': '1,2,6,1',
        'image': icon('refresh'),
        'label': 'Перезапустить приложение',
        'action': 'reload'
    }
    reload_content_btn = {
        'type': 'button',
        'layout': '1,3,6,1',
        'image': icon('refresh'),
        'label': 'Перезагрузить раздел',
        'action': 'reload:content'
    }
    reload_panel_btn = {
        'type': 'button',
        'layout': '1,4,6,1',
        'image': icon('web'),
        'label': 'Перезагрузить окно',
        'action': 'reload:panel'
    }

    if error_page:
        items = [msg, restart_app_btn]
    else:
        items = [msg, restart_app_btn, reload_content_btn, reload_panel_btn]

    return {
        'menu': [{'label': LENNY, 'data': format_action('/msx/error')}],
        'type': 'pages',
        'headline': 'Ошибка',
        'pages': [{'items': items}]
    }


def unsupported_version():
    return {
        'menu': [{'label': LENNY, 'data': format_action('/msx/too_old')}],
        'type': 'pages',
        'headline': 'Ошибка',
        'pages': [
            {
                'items': [
                    {
                        'type': 'space',
                        'layout': '0,0,8,2',
                        'color': 'msx-glass',
                        'alignment': 'center',
                        'headline': 'Старая версия MSX',
                        'text': 'Используемая версия MSX слишком старая. Выберите один из параметров ниже для обновления.',
                        'titleFooter': 'При выборе web.msx.benzac.de используйте HTTPS. После обновления настройте кинопаб снова.'
                    },
                    {
                        'type': 'button',
                        'layout': '1,2,6,1',
                        'image': icon('refresh'),
                        'label': 'Параметр id:web',
                        'action': 'start',
                        'data': {
                            'name': 'id:web',
                            'version': '2.0.3',
                            'parameter': 'content:https://msx.benzac.de/services/web.php'
                        }
                    },
                    {
                        'type': 'button',
                        'layout': '1,3,6,1',
                        'image': icon('refresh'),
                        'label': 'Параметр web.msx.benzac.de',
                        'action': 'start',
                        'data': {
                            'name': 'web.msx.benzac.de',
                            'version': '1.0.2',
                            'parameter': 'content:http://web.msx.benzac.de/msx/start.json'
                        }
                    }
                ]
            }
        ]
    }


def player_action_btn():
    return 'panel:request:player:options'


def settings_screen(screen: bool = False):
    if screen:
        return {
            'type': 'pages',
            'headline': 'Настройки',
            'caption': '/{ico:msx-blue:stop}Настройки',
            'pages': [
                {
                    'items': [
                        {
                            'type': 'button',
                            'layout': '0,0,6,4',
                            'enumerate': False,
                            'label': 'Настройки Kinopub',
                            'action': format_action('/msx/settings', module='panel'),
                            'image': icon('logo'),
                            'imageWidth': 'medium',
                            'alignment': 'center',
                            'restore': False
                        },
                        {
                            'type': 'button',
                            'layout': '6,0,6,4',
                            'enumerate': False,
                            'label': 'Настройки Media Station X',
                            'action': 'settings',
                            'image': icon('settings'),
                            'imageWidth': 'medium',
                            'alignment': 'center'
                        },
                        {
                            'type': 'button',
                            'layout': '0,4,12,2',
                            'enumerate': False,
                            'label': 'Перезапустить приложение',
                            'action': 'reload',
                            'image': icon('refresh'),
                            'imageWidth': 'medium',
                            'alignment': 'center'
                        }
                    ]
                }
            ]
        }

    return {
        'headline': 'Настройки',
        'caption': '/{ico:msx-blue:stop}Настройки',
        'template': {
            'enumerate': False,
            'type': 'control',
            'layout': '0,0,8,1'
        },
        'items': [
            {
                'label': 'Настройки Kinopub',
                'action': format_action('/msx/settings', module='panel'),
                'image': icon('logo'),
                'imageWidth': 'small',
                'restore': False
            },
            {
                'label': 'Настройки Media Station X',
                'action': 'settings',
                'image': icon('settings'),
                'imageWidth': 'small'
            },
            {
                'label': 'Перезапустить приложение',
                'action': 'reload',
                'image': icon('refresh'),
                'imageWidth': 'small'
            }
        ]
    }


def settings_menu(device_settings, user=None):
    items = []
    if user:
        info = user.get('user') or {}
        profile = info.get('profile') or {}
        entry = {
            'label': profile.get('name') or info.get('username'),
            'action': '[]',
            'imageWidth': 'small'
        }
        if profile.get('avatar'):
            entry['image'] = profile['avatar']
        days = (info.get('subscription') or {}).get('days')
        if days is not None:
            entry['extensionLabel'] = f'Подписка истекает через {int(days)} дн.'
        items.append(entry)

    items.extend([
        *device_settings.to_toggle_buttons(),
        device_settings.to_menu_msx_button()
    ])

    return {
        'type': 'list',
        'headline': 'Настройки Kinopub',
        'template': {'enumerate': False, 'type': 'control', 'layout': '0,0,8,1'},
        'items': items
    }


def stamp(cond):
    return {
        'stampColor': 'msx-glass' if cond else 'transparent',
        'stamp': '{ico:check}' if cond else '{ico:blank}'
    }


def switch(cond):
    return {
        'extensionLabel': 'Включено' if cond else 'Выключено'
    }


def label(text):
    return {'label': text}


def settings_button(id, label, action):
    return {
        'id': id,
        'label': label,
        'action': action
    }


def menu_entries_settings_panel(categories: list):
    return {
        'type': 'list',
        'headline': 'Пункты меню',
        'template': {
            'enumerate': False,
            'type': 'button',
            'layout': '0,0,4,1',
            'stampColor': 'msx-glass'
        },
        'items': [
            i.to_msx_settings_button() for i in categories if not i.hidden_from_settings
        ]
    }


def poster_settings_panel(posters):
    from models.Poster import Poster

    items = []
    i = 0
    for size in Poster.SIZES:
        for poster_proxy in Poster.PROXIES:
            items.append({
                'title': f'{size} / {poster_proxy["title"]}',
                'image': posters[i].format(size, poster_proxy['id']),
                'action': format_action(
                    f'/msx/settings/poster/set/{size}/{poster_proxy["id"]}',
                    module='execute'
                )
            })
            i += 1

    return {
        'type': 'list',
        'headline': 'Выберите первый рабочий постер',
        'template': {
            'enumerate': False,
            'type': 'separate',
            'layout': '0,0,2,4',
            'color': 'msx-glass',
            'imageFiller': 'height-center',
            'title': 'Title'
        },
        'items': items
    }


def play_action(
    video_url,
    proxy: bool = False,
    alternative_player: bool = False
):
    url = make_proxy_url(video_url) if proxy else video_url
    player_url = ALTERNATIVE_PLAYER_URL if alternative_player else PLAYER_URL

    return f'video:plugin:{player_url}?' + urlencode({'url': url})
