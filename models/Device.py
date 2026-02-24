from models.DeviceSettings import DeviceSettings
from models.KinoPub import KinoPub
from util import db


class Device:
    def __init__(self, data):
        self.id = data.get('id')
        self.code = data.get('code')
        self.token = data.get('token')
        self.refresh = data.get('refresh')
        self.kp = KinoPub(self.token, self.refresh)
        self.settings = DeviceSettings(data.get('settings'))
        self.user_agent = data.get('user_agent')

    def registered(self):
        return self.token is not None

    @classmethod
    def by_id(cls, device_id):
        entry = db.get_device_by_id(device_id)
        if entry is None:
            return None
        return cls(entry)

    @classmethod
    def create(cls, device_id):
        entry = {'id': device_id}
        db.create_device(entry)
        return cls(entry)

    def update_code(self, code):
        db.update_device_code(self.id, code)

    def update_tokens(self, token, refresh):
        db.update_device_tokens(self.id, token, refresh)
        self.token = token
        self.refresh = refresh
        self.kp = KinoPub(token, refresh)

    def update_settings(self):
        db.update_device_settings(self.id, self.settings.to_dict())

    async def notify(self):
        await self.kp.notify(self.id)

    def delete(self):
        db.delete_device(self.id)

    async def _toggle_kp_setting(self, setting_attr, kp_setting_name):
        value = not getattr(self.settings, setting_attr)
        setattr(self.settings, setting_attr, value)
        device_info = await self.kp.get_current_device_info()
        await self.kp.update_device_setting(
            device_info.id, kp_setting_name, value,
        )
        self.update_settings()

    async def _toggle_local_setting(self, setting_attr):
        setattr(
            self.settings, setting_attr,
            not getattr(self.settings, setting_attr),
        )
        self.update_settings()

    async def toggle_4k(self):
        await self._toggle_kp_setting('fourk', KinoPub.FOURK_SETTING)

    async def toggle_hdr(self):
        await self._toggle_kp_setting('hdr', KinoPub.HDR_SETTING)

    async def toggle_hevc(self):
        await self._toggle_kp_setting('hevc', KinoPub.HEVC_SETTING)

    async def toggle_mixed_playlist(self):
        await self._toggle_kp_setting(
            'mixed_playlist', KinoPub.MIXED_PLAYLIST_SETTING,
        )

    async def toggle_proxy(self):
        await self._toggle_local_setting('proxy')

    async def toggle_alternative_player(self):
        await self._toggle_local_setting('alternative_player')

    async def toggle_small_posters(self):
        await self._toggle_local_setting('small_posters')

    async def toggle_server(self) -> str:
        device_info = await self.kp.get_current_device_info()
        available_servers = await self.kp.get_available_servers()

        new_server = available_servers[0]
        for i, server in enumerate(available_servers):
            if server.name == self.settings.server and i + 1 != len(available_servers):
                new_server = available_servers[i + 1]
                break

        await self.kp.update_device_setting(
            device_info.id, KinoPub.SERVER_LOCATION_SETTING, new_server.id,
        )
        self.settings.server = new_server.name
        self.update_settings()

        return f'\u0421\u0435\u0440\u0432\u0435\u0440: {new_server.name}'

    def toggle_menu_entry(self, menu_entry):
        if menu_entry in self.settings.menu_blacklist:
            self.settings.menu_blacklist.remove(menu_entry)
        else:
            self.settings.menu_blacklist.append(menu_entry)
        self.update_settings()
        return menu_entry not in self.settings.menu_blacklist

    def reset_menu(self):
        self.settings.menu_blacklist = []
        self.update_settings()

    def update_user_agent(self, user_agent):
        db.update_device_user_agent(self.id, user_agent)
