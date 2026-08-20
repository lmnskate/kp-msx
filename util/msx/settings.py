from util.msx.core import format_action, icon


def _player_switch_button(
    alternative_player: bool,
    layout: str | None = None
):
    # The label directly shows the currently active player; pressing it toggles
    # the alternative_player setting and reloads the app.
    label = 'Переключить на основной источник' if alternative_player else 'Переключить на альтернативный источник'
    entry = {
        'label': label,
        'action': format_action(
            '/msx/settings/toggle_player',
            module='execute'
        ),
        'image': icon('spanner'),
        'enumerate': False
    }

    if layout is not None:
        entry['type'] = 'button'
        entry['layout'] = layout
        entry['imageWidth'] = 'medium'
        entry['alignment'] = 'center'
    else:
        entry['imageWidth'] = 'small'

    return entry


def settings_screen(
    screen: bool = False,
    device_settings=None
):
    alternative_player = device_settings.alternative_player if device_settings else False

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
                            'layout': '0,0,6,2',
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
                            'layout': '6,0,6,2',
                            'enumerate': False,
                            'label': 'Настройки Media Station X',
                            'action': 'settings',
                            'image': icon('settings'),
                            'imageWidth': 'medium',
                            'alignment': 'center'
                        },
                        _player_switch_button(
                            alternative_player,
                            layout='0,2,12,2'
                        ),
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

    items = [
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
        _player_switch_button(alternative_player),
        {
            'label': 'Перезапустить приложение',
            'action': 'reload',
            'image': icon('refresh'),
            'imageWidth': 'small'
        }
    ]

    return {
        'headline': 'Настройки',
        'caption': '/{ico:msx-blue:stop}Настройки',
        'template': {
            'enumerate': False,
            'type': 'control',
            'layout': '0,0,8,1'
        },
        'items': items
    }


def settings_menu(
    device_settings,
    user=None
):
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

    alternative_player_info = {
        'label': 'Альтернативный плеер',
        'action': '[]',
        'extensionLabel': (
            'Включен'
            if device_settings.alternative_player
            else 'Отключен'
        )
    }

    items.append(alternative_player_info)

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


def stamp(
    cond
):
    return {
        'stampColor': 'msx-glass' if cond else 'transparent',
        'stamp': '{ico:check}' if cond else '{ico:blank}'
    }


def switch(
    cond
):
    return {
        'extensionLabel': 'Включено' if cond else 'Выключено'
    }


def label(
    text
):
    return {'label': text}


def settings_button(
    id,
    label,
    action
):
    return {
        'id': id,
        'label': label,
        'action': action
    }


def menu_entries_settings_panel(
    categories: list
):
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


def poster_settings_panel(
    posters
):
    from models.Poster import Poster

    if not posters:
        return {
            'type': 'list',
            'headline': 'Нет постеров для отображения',
            'items': []
        }

    items = []

    for size in Poster.SIZES:
        for poster_proxy in Poster.PROXIES:
            items.append({
                'title': f'{size} / {poster_proxy["title"]}',
                'image': posters[len(items) % len(posters)].format(
                    size,
                    poster_proxy['id']
                ),
                'action': format_action(
                    f'/msx/settings/poster/set/{size}/{poster_proxy["id"]}',
                    module='execute'
                )
            })

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
