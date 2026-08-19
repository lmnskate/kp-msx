from urllib.parse import urlencode

from config.globals import LENNY, SAD_LENNY
from config.settings import server

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


def icon(
    name
):
    return f'{server.base_url}/icons/{name}.svg'


def format_action(
    path: str,
    params: dict | None = None,
    interaction: str | None = None,
    options: str | None = None,
    module: str | None = None
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


def build_list(
    layout,
    items,
    *,
    template_extra=None,
    **kwargs
):
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


def empty_item():
    return {
        'type': 'default',
        'layout': '0,0,12,1',
        'color': 'msx-glass',
        'alignment': 'center',
        'label': SAD_LENNY,
        'titleFooter': 'Здесь пока ничего нет',
        'action': '[]'
    }


def update_panel(
    content_id,
    value
):
    return {
        'response': {
            'status': 200,
            'data': {'action': f'update:panel:{content_id}', 'data': value}
        }
    }


def empty_response():
    return {'response': {'status': 200, 'data': {'action': '[]'}}}


def restart():
    return {'response': {'status': 200, 'data': {'action': 'reload'}}}


def handle_exception(
    error_page=False
):
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
