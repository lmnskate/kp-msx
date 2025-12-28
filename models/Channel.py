from urllib.parse import urlencode

import config
from util.proxy import make_proxy_url


class Channel:

    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.name = data.get('name')
        logos = data.get('logos') or {}
        self.logo = logos.get('l') or logos.get('m') or logos.get('s')
        self.stream = data.get('stream')

    def to_msx(self, proxy: bool = False, alternative_player: bool = False):
        if proxy:
            url = make_proxy_url(self.stream)
        else:
            url = self.stream

        if alternative_player:
            player = config.ALTERNATIVE_PLAYER
        else:
            player = config.PLAYER

        if config.TIZEN:
            action = f'video:{self.stream}'
        else:
            action = f"video:plugin:{player}?" + urlencode({'url': url})

        entry = {
            'title': self.title,
            'playerLabel': self.title,
            'image': self.logo,
            "action": action
        }
        return entry
