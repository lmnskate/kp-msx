from config.globals import (HDR_ID, HEVC_ID, MENU_ID, PINNED_MENU_ENTRIES,
                            SWITCH_IDS, UHD_ID)
from util import msx

TOGGLE_BUTTONS = [
    (UHD_ID, '4K', 'uhd'),
    (HDR_ID, 'HDR', 'hdr'),
    (HEVC_ID, 'HEVC', 'hevc')
]


class DeviceSettings:
    def __init__(
        self,
        data
    ):
        if data is None:
            data = {}

        # Pinned entries stored by older versions are dropped on load
        self.menu_blacklist = [
            entry for entry in data.get('menu_blacklist', [])
            if entry not in PINNED_MENU_ENTRIES
        ]
        self.uhd = data.get('uhd', False)
        self.proxy = data.get('proxy', False)
        self.alternative_player = data.get('alternative_player', False)
        self.hevc = data.get('hevc', False)
        self.hdr = data.get('hdr', False)
        self.poster_size = data.get('poster_size')
        if self.poster_size is None:
            self.poster_size = 'small' if data.get('small_posters', False) else 'big'
        self.poster_proxy = data.get('poster_proxy')

    def to_dict(
        self
    ):
        return {
            'menu_blacklist': self.menu_blacklist,
            'uhd': self.uhd,
            'proxy': self.proxy,
            'alternative_player': self.alternative_player,
            'hevc': self.hevc,
            'hdr': self.hdr,
            'poster_size': self.poster_size,
            'poster_proxy': self.poster_proxy
        }

    def toggle_button(
        self,
        setting_id,
        label,
        value
    ):
        entry = msx.settings_button(
            setting_id,
            label,
            msx.format_action(
                f'/msx/settings/toggle/{setting_id}',
                module='execute'
            )
        )
        if setting_id in SWITCH_IDS:
            entry.update(msx.switch(value))
        else:
            entry.update(msx.stamp(value))

        return entry

    def to_toggle_buttons(
        self
    ):
        return [
            self.toggle_button(
                setting_id,
                label,
                getattr(self, attr)
            )
            for setting_id, label, attr in TOGGLE_BUTTONS
        ]

    def to_menu_msx_button(
        self
    ):
        return msx.settings_button(
            MENU_ID,
            'Пункты меню',
            msx.format_action(
                '/msx/settings/menu_entries',
                module='panel'
            )
        )
