from models.Playable import Playable
from util import msx


class Video(Playable):
    def __init__(
        self,
        data,
        content_id,
        content_title
    ):
        super().__init__(data)

        self.content_id = content_id
        self.content_title = content_title

        self.title = data.get('title')

    def to_multivideo_entry(
        self,
        proxy: bool = False,
        alternative_player: bool = False,
        device_settings=None,
        audio_tracks=None
    ):
        properties = self.msx_properties(
            proxy=proxy,
            alternative_player=alternative_player
        )

        if audio_tracks:
            properties['html5x:audiotrack:count'] = str(len(audio_tracks))
            for index, track in enumerate(audio_tracks):
                prefix = f'html5x:audiotrack:{index}'
                if track.get('language'):
                    properties[f'{prefix}:language'] = track['language']
                if track.get('name'):
                    properties[f'{prefix}:name'] = track['name']
                if track.get('group'):
                    properties[f'{prefix}:group'] = track['group']
                properties[f'{prefix}:default'] = 'YES' if track.get('default') else 'NO'

        return {
            'title': self.title,
            'titleFooter': self.footer(),
            'progress': self.progress(),
            'image': self.thumbnail,
            'playerLabel': self.content_title,
            'action': self.msx_action(
                proxy=proxy,
                alternative_player=alternative_player
            ),
            'properties': properties
        }

    def trigger_ready(
        self
    ):
        return msx.format_action(
            path='/msx/play',
            params={
                'content_id': self.content_id
            },
            module='execute'
        )

    def resume_key(
        self
    ):
        return f'{self.content_id} {self.player_title()} {self.title}'

    def player_title(
        self
    ):
        return self.content_title
