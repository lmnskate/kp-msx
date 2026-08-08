from util import msx
from util.proxy import remember_url


class Channel:
    def __init__(
        self,
        data
    ):
        self.id = data.get('id')
        self.title = data.get('title')
        self.name = data.get('name')
        logos = data.get('logos') or {}
        self.logo = logos.get('l') or logos.get('m') or logos.get('s')
        remember_url(self.logo)
        self.stream = data.get('stream')

    def to_msx(
        self,
        alternative_player: bool = False
    ):
        return {
            'title': self.title,
            'playerLabel': self.title,
            'image': self.logo,
            'badge': 'LIVE',
            'badgeColor': 'msx-red',
            'action': msx.play_action(
                self.stream,
                alternative_player=alternative_player
            )
        }
