from models.Playable import _progress_pct


class Media:
    def __init__(
        self,
        data,
        time=None
    ):
        self.title = data.get('title')
        self.n = data.get('number')
        self.season = data.get('snumber')
        self.duration = data.get('duration')
        self.time = time

    def to_subtitle(
        self
    ):
        return f'[S{self.season}/E{self.n}] {self.title}'

    def progress(
        self
    ):
        return _progress_pct(
            self.duration,
            self.time
        )
