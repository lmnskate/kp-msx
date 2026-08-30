from models.Playable import Playable


class Episode(Playable):
    def __init__(
        self,
        data,
        content_id,
        season
    ):
        super().__init__(data)

        self.content_id = content_id
        self.season = season

        self.n = data.get('number')
        self.title = data.get('title')

        self.watched = data.get('watched') == 1

    def menu_title(
        self
    ):
        title = self.title or 'Серия'

        return f'{self.n}. {title}'

    def player_title(
        self
    ):
        title = self.title or 'Серия'

        return f'[S{self.season}/E{self.n}] {title}'

    def resume_key(
        self
    ):
        return f'{self.content_id} {self.player_title()}'
