import config.globals as g
from models.DeviceSettings import DeviceSettings
from models.KinoPub import KinoPub
from util import db

KP_TOGGLES = {
    g.UHD_ID: ('uhd', g.UHD_SETTING),
    g.HDR_ID: ('hdr', g.HDR_SETTING),
    g.HEVC_ID: ('hevc', g.HEVC_SETTING),
    g.MIXED_PLAYLIST_ID: ('mixed_playlist', g.MIXED_PLAYLIST_SETTING),
}

LOCAL_TOGGLES = {
    g.PROXY_ID: 'proxy',
    g.ALTERNATIVE_PLAYER_ID: 'alternative_player',
}


class Device:
    def __init__(
        self,
        data
    ):
        self.id = data.get('id')
        self.code = data.get('code')
        self.token = data.get('token')
        self.refresh = data.get('refresh')
        self.kp = KinoPub(
            self.token,
            self.refresh,
            self.id
        )
        self.settings = DeviceSettings(data.get('settings'))
        self.user_agent = data.get('user_agent')

    def registered(
        self
    ):
        return self.token is not None

    @classmethod
    def by_id(
        cls,
        device_id
    ):
        entry = db.get_device_by_id(device_id)
        if entry is None:
            return None

        return cls(entry)

    @classmethod
    def create(
        cls,
        device_id
    ):
        entry = db.create_device({'id': device_id})
        if entry is None:
            entry = db.get_device_by_id(device_id)

        return cls(entry)

    def update_code(
        self,
        code
    ):
        db.update_device_code(
            self.id,
            code
        )

    async def update_tokens(
        self,
        token,
        refresh
    ):
        if self.kp is not None:
            await self.kp.close_session()

        db.update_device_tokens(
            self.id,
            token,
            refresh
        )
        self.token = token
        self.refresh = refresh
        self.kp = KinoPub(
            token,
            refresh,
            self.id
        )

    def update_settings(
        self
    ):
        db.update_device_settings(
            self.id,
            self.settings.to_dict()
        )

    async def notify(
        self
    ):
        await self.kp.notify(self.id)

    def delete(
        self
    ):
        db.delete_device(self.id)

    async def toggle(
        self,
        setting_id
    ):
        if setting_id in KP_TOGGLES:
            attr, kp_setting = KP_TOGGLES[setting_id]
            value = not getattr(self.settings, attr)
            setattr(self.settings, attr, value)
            self.update_settings()
            # Best-effort sync to the KinoPub device settings; the local
            # value is the source of truth even if the API call fails.
            device_info = await self.kp.get_current_device_info()
            if device_info is not None:
                await self.kp.update_device_setting(
                    device_info.id,
                    kp_setting,
                    value
                )

            return attr

        if setting_id in LOCAL_TOGGLES:
            attr = LOCAL_TOGGLES[setting_id]
            setattr(
                self.settings,
                attr,
                not getattr(self.settings, attr)
            )
            self.update_settings()

            return attr

    async def toggle_server(
        self
    ) -> 'str | None':
        device_info = await self.kp.get_current_device_info()
        if device_info is None:
            return None

        available_servers = await self.kp.get_available_servers()
        if not available_servers:
            return None

        new_server = available_servers[0]
        for i, server in enumerate(available_servers):
            if server.name == self.settings.server and i + 1 != len(available_servers):
                new_server = available_servers[i + 1]
                break

        await self.kp.update_device_setting(
            device_info.id,
            g.SERVER_LOCATION_SETTING,
            new_server.id
        )
        self.settings.server = new_server.name
        self.update_settings()

        return f'Сервер: {new_server.name}'

    def toggle_menu_entry(
        self,
        menu_entry
    ):
        if menu_entry in self.settings.menu_blacklist:
            self.settings.menu_blacklist.remove(menu_entry)
        else:
            self.settings.menu_blacklist.append(menu_entry)
        self.update_settings()

        return menu_entry not in self.settings.menu_blacklist

    def reset_menu(
        self
    ):
        self.settings.menu_blacklist = []
        self.update_settings()

    def set_poster_settings(
        self,
        poster_size,
        poster_proxy
    ):
        self.settings.poster_size = poster_size
        self.settings.poster_proxy = poster_proxy
        self.update_settings()

    def update_user_agent(
        self,
        user_agent
    ):
        db.update_device_user_agent(
            self.id,
            user_agent
        )
