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
        if not self.time or not self.duration or self.time >= self.duration:
            return None
        return round(100 * self.time / self.duration)
