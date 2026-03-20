from config.globals import (ALTERNATIVE_PLAYER_ID, ALTERNATIVE_PLAYER_URL,
                            FOURK_ID, HDR_ID, HELP_ID, HEVC_ID, LENNY, MENU_ID,
                            MIXED_PLAYLIST_ID, PLAYER_URL, PROXY_ID, SERVER_ID,
                            SMALL_POSTERS_ID)
from config.settings import kp
from util import msx

TOGGLE_BUTTONS = [
    (FOURK_ID, '4K', 'fourk',
     'Выключатель 4К. Если телевизор старый, слабый или дешёвый, то лучше не включать.'),
    (HDR_ID, 'HDR', 'hdr',
     'Выключатель HDR. Если телевизор старый, слабый или дешёвый, то лучше не включать.'),
    (HEVC_ID, 'HEVC', 'hevc',
     'Выключатель HEVC. Если телевизор старый, слабый или дешёвый, то лучше не включать.'),
    (MIXED_PLAYLIST_ID, 'Смешанный плейлист', 'mixed_playlist',
     'Выключатель смешанного плейлиста. Если телевизор старый, слабый или дешёвый, то лучше не включать.'),
    (PROXY_ID, 'Прокси для плейлиста', 'proxy',
     'Включите, если видео не загружаются вообще (нет длительности, нет дорожек и субтитров в настройках плеера).'),
    (ALTERNATIVE_PLAYER_ID, 'Альтернативный плеер', 'alternative_player',
     'Включите, если телевизор очень старый (Tizen или webOS до 3 версии, год выпуска ТВ до 2018 года).'),
    (SMALL_POSTERS_ID, 'Ремонт постеров', 'small_posters',
     'Включите, если постеры не загружаются. Требуется перезапуск приложения.'),
]


class DeviceSettings:
    def __init__(self, data):
        if data is None:
            data = {}

        self.menu_blacklist = data.get('menu_blacklist', [])
        self.fourk = data.get('fourk', False)
        self.proxy = data.get('proxy', False)
        self.alternative_player = data.get('alternative_player', False)
        self.hevc = data.get('hevc', False)
        self.hdr = data.get('hdr', False)
        self.mixed_playlist = data.get('mixed_playlist', False)
        self.small_posters = data.get('small_posters', False)
        self.server = data.get('server', LENNY)

    def to_dict(self):
        return {
            'menu_blacklist': self.menu_blacklist,
            'fourk': self.fourk,
            'proxy': self.proxy,
            'alternative_player': self.alternative_player,
            'hevc': self.hevc,
            'hdr': self.hdr,
            'mixed_playlist': self.mixed_playlist,
            'small_posters': self.small_posters,
            'server': self.server
        }

    def toggle_button(self, setting_id, label, hint, value):
        entry = msx.settings_button(
            setting_id,
            label,
            msx.format_action(
                f'/msx/settings/toggle/{setting_id}', module='execute'
            ),
            hint
        )
        entry.update(msx.stamp(value))
        return entry

    def to_toggle_buttons(self):
        return [
            self.toggle_button(
                setting_id,
                label,
                hint,
                getattr(self, attr)
            )
            for setting_id, label, attr, hint in TOGGLE_BUTTONS
        ]

    def to_server_msx_button(self):
        return msx.settings_button(
            SERVER_ID,
            f'Сервер: {self.server}',
            msx.format_action(
                f'/msx/settings/toggle/{SERVER_ID}', module='execute'
            ),
            'Переключатель сервера. Для определения лучшего сервера используйте zamerka.com.'
        )

    def to_menu_msx_button(self):
        return msx.settings_button(
            MENU_ID,
            'Пункты меню',
            msx.format_action('/msx/settings/menu_entries', module='panel'),
            'Здесь можно выключить или включить разделы главного меню слева. После изменения потребуется перезапустить приложение'
        )

    def to_help_msx_button(self):
        return msx.settings_button(
            HELP_ID,
            'Справка',
            '[]',
            'Исходный код: https://github.com/lmnskate/kp-msx\n'
            f'Плеер: {PLAYER_URL}\n'
            f'Альтернативный плеер: {ALTERNATIVE_PLAYER_URL}\n'
            f'Протокол: {kp.protocol}'
        )
