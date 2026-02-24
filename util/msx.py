from urllib.parse import urlencode

import config
from util.proxy import make_proxy_url

LENNY = '¯\\_(ツ)_/¯'
SAD_LENNY = '(◡︵◡)'


def icon(name):
    return f'{config.MSX_HOST}/icons/{name}.svg'


def format_action(
    path: str,
    params: dict = None,
    interaction: str = None,
    options: str = None,
    module: str = None,
):
    if params is None:
        params = {}
    params.update({'id': '{ID}'})

    if path.startswith('/'):
        data = f'{config.MSX_HOST}{path}'
    else:
        data = path

    data = data + '?' + urlencode(params, safe='{}')

    if interaction:
        if interaction.startswith('/'):
            interaction = f'{config.MSX_HOST}{interaction}'

        data = 'request:interaction:' + data
        if options:
            data = data + '|' + options
        data = data + '@' + interaction

    if module:
        data = module + ':' + data

    return data


def start():
    return {
        'name': 'Kinopub',
        'version': '6.6.6',
        'parameter': format_action('/msx/menu', module='menu'),
        'welcome': 'none',
        'launcher': {
            'parameter': format_action('/msx/menu', module='menu'),
            'image': icon('logo'),
            'color': 'none',
        },
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
                'data': format_action('/msx/registration'),
            }
        ],
    }


def registered_menu(categories: list):
    menu = list(
        category.to_msx()
        for category in (categories or [])
        if not category.blacklisted
    )
    if len(menu) == 0:
        menu = [sad_screen()]
    return {
        'reuse': False,
        'cache': False,
        'restore': False,
        'refocus': 1,
        'headline': 'Kinopub',
        'options': settings_screen(),
        'menu': menu,
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
                            'text': 'Вы выключили все разделы меню, поэтому теперь здесь ничего нет.',
                        },
                        {
                            'type': 'button',
                            'layout': '2,3,4,1',
                            'image': icon('refresh'),
                            'label': 'Вернуть назад',
                            'action': format_action(
                                '/msx/settings/reset_menu', module='execute',
                            ),
                        },
                    ],
                }
            ],
        },
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
                        'layout': '0,0,8,3',
                        'color': 'msx-glass',
                        'alignment': 'center',
                        'headline': '{ico:check-circle} Уже зарегистрирован',
                        'text': 'Это устройство уже привязано к аккаунту Kinopub.',
                    },
                ]
            }
        ],
    }


def registration(user_code):
    return {
        'type': 'pages',
        'headline': 'Регистрация',
        'pages': [
            {
                'items': [
                    {
                        'type': 'space',
                        'layout': '0,0,8,3',
                        'color': 'msx-glass',
                        'alignment': 'center',
                        'headline': user_code,
                        'text': 'Используйте этот код для добавления устройства на Kinopub или зеркале.',
                        'titleFooter': 'После ввода кода нажмите кнопку ниже.',
                    },
                    {
                        'type': 'button',
                        'layout': '2,3,4,1',
                        'image': icon('check'),
                        'label': 'Я ввёл код',
                        'action': format_action(
                            '/msx/check_registration', module='execute',
                        ),
                    },
                ]
            }
        ],
    }


def code_not_entered():
    return {
        'response': {
            'status': 200,
            'data': {
                'action': 'warn:Код не введён. Если прошло больше 5 минут, перезапустите приложение для получения нового кода.'
            },
        }
    }


def restart():
    return {'response': {'status': 200, 'data': {'action': 'reload'}}}


def content_list(
    entries,
    *,
    category=None,
    page=1,
    show_header=False,
    decompress=None,
    small_posters=False,
):
    resp = {
        'type': 'list',
        'preload': 'next',
        'template': {
            'type': 'separate',
            'layout': '0,0,2,4',
            'color': 'msx-glass',
            'imageFiller': 'height-center',
            'imageOverlay': 2,
            'title': 'Title',
        },
        'items': list(entry.to_msx(small_poster=small_posters) for entry in entries),
    }

    if decompress is not None:
        resp['template']['decompress'] = decompress

    if show_header and page == 1:
        from models.CategoryExtra import CategoryExtra

        resp['header'] = {
            'items': list(
                i.to_msx(category) for i in CategoryExtra.static_extras()
            ),
        }

    return resp


def collections(entries, *, small_posters=False):
    return {
        'type': 'list',
        'preload': 'next',
        'template': {
            'type': 'separate',
            'layout': '0,0,3,6',
            'color': 'msx-glass',
            'imageFiller': 'height-center',
            'imageOverlay': 3,
            'title': 'Title',
        },
        'items': list(entry.to_msx(small_poster=small_posters) for entry in entries),
    }


def bookmark_folders(result):
    return {
        'type': 'list',
        'headline': 'Закладки',
        'template': {
            'type': 'separate',
            'layout': '0,0,4,1',
            'color': 'msx-glass',
        },
        'items': list(i.to_msx() for i in result),
    }


def genre_folders(category, result):
    return {
        'type': 'list',
        'headline': 'Жанры',
        'template': {
            'type': 'separate',
            'layout': '0,0,4,1',
            'color': 'msx-glass',
        },
        'items': list(i.to_msx(category) for i in result),
    }


def update_panel(content_id, value):
    return {
        'response': {
            'status': 200,
            'data': {'action': f'update:panel:{content_id}', 'data': value},
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
                    'action': '[]',
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
                'button:restart:image': icon('settings'),
                'button:restart:action': player_action_btn(),
                'progress:display': 'false',
            },
        },
        'items': [
            channel.to_msx(alternative_player=alternative_player)
            for channel in channels
        ],
    }


def handle_exception(error_page=False):
    msg = {
        'type': 'space',
        'layout': '0,0,8,2',
        'color': 'msx-glass',
        'alignment': 'center',
        'headline': 'Произошла ошибка загрузки',
        'text': 'Скорее всего, кинопаб сейчас недоступен. Проверьте статус на kinopub.online и ожидайте ремонта.',
    }
    restart_app_btn = {
        'type': 'button',
        'layout': '1,2,6,1',
        'image': icon('refresh'),
        'label': 'Перезапустить приложение',
        'action': 'reload',
    }
    reload_content_btn = {
        'type': 'button',
        'layout': '1,3,6,1',
        'image': icon('refresh'),
        'label': 'Перезагрузить раздел',
        'action': 'reload:content',
    }
    reload_panel_btn = {
        'type': 'button',
        'layout': '1,4,6,1',
        'image': icon('web'),
        'label': 'Перезагрузить окно',
        'action': 'reload:panel',
    }

    if error_page:
        items = [msg, restart_app_btn]
    else:
        items = [msg, restart_app_btn, reload_content_btn, reload_panel_btn]

    return {
        'menu': [{'label': LENNY, 'data': format_action('/msx/error')}],
        'type': 'pages',
        'headline': 'Ошибка',
        'pages': [{'items': items}],
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
                        'titleFooter': 'При выборе web.msx.benzac.de используйте HTTPS. После обновления настройте кинопаб снова.',
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
                            'parameter': 'content:https://msx.benzac.de/services/web.php',
                        },
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
                            'parameter': 'content:http://web.msx.benzac.de/msx/start.json',
                        },
                    },
                ]
            }
        ],
    }


def player_action_btn():
    if config.TIZEN:
        return 'content:request:interaction:init@https://msx.benzac.de/interaction/tizen.html'
    return 'panel:request:player:options'


DEFAULT_PLAY_BUTTON_PROPS = {
    'control:type': 'extended',
    'button:content:image': icon('list'),
    'button:content:action': 'player:content',
    'button:restart:image': icon('settings'),
    'button:restart:action': player_action_btn(),
    'button:speed:image': icon('replay'),
    'button:speed:action': 'player:restart',
}

FOURK_ID = 'fourk'
HDR_ID = 'hdr'
HEVC_ID = 'hevc'
MIXED_PLAYLIST_ID = 'mixed_playlist'
SERVER_ID = 'server'
PROXY_ID = 'proxy'
ALTERNATIVE_PLAYER_ID = 'alternative_player'
SMALL_POSTERS_ID = 'small_posters'
MENU_ID = 'menu'
HELP_ID = 'help'


def settings_screen(screen: bool = False):
    entry = {
        'headline': 'Настройки',
        'caption': '/{ico:msx-blue:stop}Настройки',
        'template': {
            'enumerate': False,
            'type': 'control',
            'layout': '0,0,6,1' if screen else '0,0,8,1',
        },
        'items': [
            {
                'label': 'Настройки Kinopub',
                'action': format_action('/msx/settings', module='panel'),
                'image': icon('logo'),
                'imageWidth': 'small',
                'restore': False,
            },
            {
                'label': 'Настройки Media Station X',
                'action': 'settings',
                'image': icon('settings'),
                'imageWidth': 'small',
            },
            {
                'label': 'Перезапустить приложение',
                'action': 'reload',
                'image': icon('refresh'),
                'imageWidth': 'small',
            },
        ],
    }

    if screen:
        entry['items'].append(
            {
                'position': 'context:context1',
                'type': 'space',
                'id': 'info',
                'offset': '-6,1,6,1',
                'headline': 'Настройки можно также открыть из главного меню (слева) нажатием синей цветной [{ico:msx-blue:stop}] кнопки или кнопки "меню" [{ico:menu}] на пульте. Подсказка находится справа снизу экрана.\nЭтот (и любой другой) пункт меню можно скрыть в разделе "Настройки Kinopub".',
                'action': '[]',
            }
        )

    return entry


def settings_menu(device_settings):
    return {
        'headline': 'Настройки Kinopub',
        'template': {'enumerate': False, 'type': 'control', 'layout': '0,0,4,1'},
        'items': [
            device_settings.to_fourk_msx_button(),
            device_settings.to_hdr_msx_button(),
            device_settings.to_hevc_msx_button(),
            device_settings.to_mixed_playlist_msx_button(),
            device_settings.to_server_msx_button(),
            device_settings.to_proxy_msx_button(),
            device_settings.to_alternative_player_msx_button(),
            device_settings.to_small_posters_msx_button(),
            device_settings.to_menu_msx_button(),
            device_settings.to_help_msx_button(),
            {
                'position': 'context:context1',
                'type': 'space',
                'id': 'info',
                'offset': '0,0,4,1',
                'headline': '',
                'action': '[]',
            },
        ],
    }


def stamp(cond):
    return {
        'stampColor': 'msx-glass' if cond else 'transparent',
        'stamp': '{ico:check}' if cond else '{ico:blank}',
    }


def label(text):
    return {'label': text}


def settings_button(id, label, action, hint):
    return {
        'id': id,
        'label': label,
        'action': action,
        'selection': {'action': 'update:panel:info', 'data': {'headline': hint}},
    }


def menu_entries_settings_panel(categories: list):
    return {
        'type': 'list',
        'headline': 'Пункты меню',
        'template': {
            'enumerate': False,
            'type': 'button',
            'layout': '0,0,4,1',
            'stampColor': 'msx-glass',
        },
        'items': list(
            i.to_msx_settings_button() for i in categories if not i.ignored
        ),
    }


def play_action(video_url, proxy: bool = False, alternative_player: bool = False):
    url = make_proxy_url(video_url) if proxy else video_url
    player = config.ALTERNATIVE_PLAYER if alternative_player else config.PLAYER

    if config.TIZEN:
        return f'video:{url}'
    return f'video:plugin:{player}?' + urlencode({'url': url})
