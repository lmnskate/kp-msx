from models.Playable import Playable
from util import msx


class Episode(Playable):
    def __init__(self, data, content_id, season):
        super().__init__(data)

        self.content_id = content_id
        self.season = season

        self.n = data.get('number')
        self.title = data.get('title')

        self.watched = data.get('watched') == 1

    def menu_title(self):
        return f'{self.n}. {self.title}'

    def player_title(self):
        return f'[S{self.season}/E{self.n}] {self.title}'

    def trigger_ready(self):
        params = {
            'content_id': self.content_id,
            'season': self.season,
            'episode': self.n,
        }
        return msx.format_action('/msx/play', params=params, module='execute')

    def resume_key(self):
        return str(self.content_id) + ' ' + self.player_title()
