from models.Playable import Playable
from util import msx


class Video(Playable):
    def __init__(self, data, content_id, content_title):
        super().__init__(data)

        self.content_id = content_id
        self.content_title = content_title

        self.title = data.get('title')

    def to_multivideo_entry(
        self, proxy: bool = False, alternative_player: bool = False,
    ):
        return {
            'label': self.title,
            'action': self.msx_action(
                proxy=proxy, alternative_player=alternative_player,
            ),
            'properties': self.msx_properties(
                proxy=proxy, alternative_player=alternative_player,
            ),
        }

    def trigger_ready(self):
        return msx.format_action(
            '/msx/play', params={'content_id': self.content_id}, module='execute',
        )

    def resume_key(self):
        return str(self.content_id) + ' ' + self.player_title() + ' ' + self.title

    def player_title(self):
        return self.content_title
