from models.Playable import Playable


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

        self.n = data.get('number')
        self.title = data.get('title')

    def to_multivideo_entry(
        self,
        proxy: bool = False,
        alternative_player: bool = False,
        device_settings=None
    ):
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
            'properties': self.msx_properties(
                proxy=proxy,
                alternative_player=alternative_player
            )
        }

    def resume_key(
        self
    ):
        return f'{self.content_id} {self.player_title()} {self.title}'

    def player_title(
        self
    ):
        return self.content_title
