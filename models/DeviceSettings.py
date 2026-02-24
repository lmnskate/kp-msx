import config
from util import msx


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
        self.server = data.get('server', msx.LENNY)

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
            'server': self.server,
        }

    def _toggle_button(self, setting_id, label, hint, value):
        entry = msx.settings_button(
            setting_id,
            label,
            msx.format_action(
                f'/msx/settings/toggle/{setting_id}', module='execute',
            ),
            hint,
        )
        entry.update(msx.stamp(value))
        return entry

    def to_fourk_msx_button(self):
        return self._toggle_button(
            msx.FOURK_ID, '4K',
            '\u0412\u044b\u043a\u043b\u044e\u0447\u0430\u0442\u0435\u043b\u044c 4\u041a. \u0415\u0441\u043b\u0438 \u0442\u0435\u043b\u0435\u0432\u0438\u0437\u043e\u0440 \u0441\u0442\u0430\u0440\u044b\u0439, \u0441\u043b\u0430\u0431\u044b\u0439 \u0438\u043b\u0438 \u0434\u0435\u0448\u0451\u0432\u044b\u0439, \u0442\u043e \u043b\u0443\u0447\u0448\u0435 \u043d\u0435 \u0432\u043a\u043b\u044e\u0447\u0430\u0442\u044c.',
            self.fourk,
        )

    def to_hdr_msx_button(self):
        return self._toggle_button(
            msx.HDR_ID, 'HDR',
            '\u0412\u044b\u043a\u043b\u044e\u0447\u0430\u0442\u0435\u043b\u044c HDR. \u0415\u0441\u043b\u0438 \u0442\u0435\u043b\u0435\u0432\u0438\u0437\u043e\u0440 \u0441\u0442\u0430\u0440\u044b\u0439, \u0441\u043b\u0430\u0431\u044b\u0439 \u0438\u043b\u0438 \u0434\u0435\u0448\u0451\u0432\u044b\u0439, \u0442\u043e \u043b\u0443\u0447\u0448\u0435 \u043d\u0435 \u0432\u043a\u043b\u044e\u0447\u0430\u0442\u044c.',
            self.hdr,
        )

    def to_hevc_msx_button(self):
        return self._toggle_button(
            msx.HEVC_ID, 'HEVC',
            '\u0412\u044b\u043a\u043b\u044e\u0447\u0430\u0442\u0435\u043b\u044c HEVC. \u0415\u0441\u043b\u0438 \u0442\u0435\u043b\u0435\u0432\u0438\u0437\u043e\u0440 \u0441\u0442\u0430\u0440\u044b\u0439, \u0441\u043b\u0430\u0431\u044b\u0439 \u0438\u043b\u0438 \u0434\u0435\u0448\u0451\u0432\u044b\u0439, \u0442\u043e \u043b\u0443\u0447\u0448\u0435 \u043d\u0435 \u0432\u043a\u043b\u044e\u0447\u0430\u0442\u044c.',
            self.hevc,
        )

    def to_mixed_playlist_msx_button(self):
        return self._toggle_button(
            msx.MIXED_PLAYLIST_ID, '\u0421\u043c\u0435\u0448\u0430\u043d\u043d\u044b\u0439 \u043f\u043b\u0435\u0439\u043b\u0438\u0441\u0442',
            '\u0412\u044b\u043a\u043b\u044e\u0447\u0430\u0442\u0435\u043b\u044c \u0441\u043c\u0435\u0448\u0430\u043d\u043d\u043e\u0433\u043e \u043f\u043b\u0435\u0439\u043b\u0438\u0441\u0442\u0430. \u0415\u0441\u043b\u0438 \u0442\u0435\u043b\u0435\u0432\u0438\u0437\u043e\u0440 \u0441\u0442\u0430\u0440\u044b\u0439, \u0441\u043b\u0430\u0431\u044b\u0439 \u0438\u043b\u0438 \u0434\u0435\u0448\u0451\u0432\u044b\u0439, \u0442\u043e \u043b\u0443\u0447\u0448\u0435 \u043d\u0435 \u0432\u043a\u043b\u044e\u0447\u0430\u0442\u044c.',
            self.mixed_playlist,
        )

    def to_proxy_msx_button(self):
        return self._toggle_button(
            msx.PROXY_ID, '\u041f\u0440\u043e\u043a\u0441\u0438 \u0434\u043b\u044f \u043f\u043b\u0435\u0439\u043b\u0438\u0441\u0442\u0430',
            '\u0412\u043a\u043b\u044e\u0447\u0438\u0442\u0435, \u0435\u0441\u043b\u0438 \u0432\u0438\u0434\u0435\u043e \u043d\u0435 \u0437\u0430\u0433\u0440\u0443\u0436\u0430\u044e\u0442\u0441\u044f \u0432\u043e\u043e\u0431\u0449\u0435 (\u043d\u0435\u0442 \u0434\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u0438, \u043d\u0435\u0442 \u0434\u043e\u0440\u043e\u0436\u0435\u043a \u0438 \u0441\u0443\u0431\u0442\u0438\u0442\u0440\u043e\u0432 \u0432 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430\u0445 \u043f\u043b\u0435\u0435\u0440\u0430).',
            self.proxy,
        )

    def to_alternative_player_msx_button(self):
        return self._toggle_button(
            msx.ALTERNATIVE_PLAYER_ID, '\u0410\u043b\u044c\u0442\u0435\u0440\u043d\u0430\u0442\u0438\u0432\u043d\u044b\u0439 \u043f\u043b\u0435\u0435\u0440',
            '\u0412\u043a\u043b\u044e\u0447\u0438\u0442\u0435, \u0435\u0441\u043b\u0438 \u0442\u0435\u043b\u0435\u0432\u0438\u0437\u043e\u0440 \u043e\u0447\u0435\u043d\u044c \u0441\u0442\u0430\u0440\u044b\u0439 (Tizen \u0438\u043b\u0438 webOS \u0434\u043e 3 \u0432\u0435\u0440\u0441\u0438\u0438, \u0433\u043e\u0434 \u0432\u044b\u043f\u0443\u0441\u043a\u0430 \u0422\u0412 \u0434\u043e 2018 \u0433\u043e\u0434\u0430).',
            self.alternative_player,
        )

    def to_small_posters_msx_button(self):
        return self._toggle_button(
            msx.SMALL_POSTERS_ID, '\u0420\u0435\u043c\u043e\u043d\u0442 \u043f\u043e\u0441\u0442\u0435\u0440\u043e\u0432',
            '\u0412\u043a\u043b\u044e\u0447\u0438\u0442\u0435, \u0435\u0441\u043b\u0438 \u043f\u043e\u0441\u0442\u0435\u0440\u044b \u043d\u0435 \u0437\u0430\u0433\u0440\u0443\u0436\u0430\u044e\u0442\u0441\u044f. \u0422\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044f \u043f\u0435\u0440\u0435\u0437\u0430\u043f\u0443\u0441\u043a \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f.',
            self.small_posters,
        )

    def to_server_msx_button(self):
        return msx.settings_button(
            msx.SERVER_ID,
            f'\u0421\u0435\u0440\u0432\u0435\u0440: {self.server}',
            msx.format_action(
                f'/msx/settings/toggle/{msx.SERVER_ID}', module='execute',
            ),
            '\u041f\u0435\u0440\u0435\u043a\u043b\u044e\u0447\u0430\u0442\u0435\u043b\u044c \u0441\u0435\u0440\u0432\u0435\u0440\u0430. \u0414\u043b\u044f \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u044f \u043b\u0443\u0447\u0448\u0435\u0433\u043e \u0441\u0435\u0440\u0432\u0435\u0440\u0430 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435 zamerka.com.',
        )

    def to_menu_msx_button(self):
        return msx.settings_button(
            msx.MENU_ID,
            '\u041f\u0443\u043d\u043a\u0442\u044b \u043c\u0435\u043d\u044e',
            msx.format_action('/msx/settings/menu_entries', module='panel'),
            '\u0417\u0434\u0435\u0441\u044c \u043c\u043e\u0436\u043d\u043e \u0432\u044b\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u0438\u043b\u0438 \u0432\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u0440\u0430\u0437\u0434\u0435\u043b\u044b \u0433\u043b\u0430\u0432\u043d\u043e\u0433\u043e \u043c\u0435\u043d\u044e \u0441\u043b\u0435\u0432\u0430. \u041f\u043e\u0441\u043b\u0435 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u043f\u043e\u0442\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044f \u043f\u0435\u0440\u0435\u0437\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435',
        )

    def to_help_msx_button(self):
        return msx.settings_button(
            msx.HELP_ID,
            '\u0421\u043f\u0440\u0430\u0432\u043a\u0430',
            '[]',
            '\u0418\u0441\u0445\u043e\u0434\u043d\u044b\u0439 \u043a\u043e\u0434: https://github.com/lmnskate/kp-msx\n'
            f'\u041f\u043b\u0435\u0435\u0440: {config.PLAYER}\n'
            f'\u0410\u043b\u044c\u0442\u0435\u0440\u043d\u0430\u0442\u0438\u0432\u043d\u044b\u0439 \u043f\u043b\u0435\u0435\u0440: {config.ALTERNATIVE_PLAYER}\n'
            f'\u041f\u0440\u043e\u0442\u043e\u043a\u043e\u043b: {config.PROTOCOL}',
        )
