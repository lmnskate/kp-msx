from urllib.parse import urlencode

import config


class Channel:
    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.name = data.get('name')
        logos = data.get('logos') or {}
        self.logo = logos.get('l') or logos.get('m') or logos.get('s')
        self.stream = data.get('stream')

    def to_msx(self, alternative_player: bool = False):
        if alternative_player:
            player = config.ALTERNATIVE_PLAYER
        else:
            player = config.PLAYER

        if config.TIZEN:
            action = f'video:{self.stream}'
        else:
            action = f'video:plugin:{player}?' + urlencode({'url': self.stream})

        return {
            'title': self.title,
            'playerLabel': self.title,
            'image': self.logo,
            'action': action,
        }
