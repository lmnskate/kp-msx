from models.Episode import Episode


class Season:
    def __init__(
        self,
        data,
        content_id
    ):
        self.content_id = content_id

        self.n = data.get('number')
        self.id = data.get('id')
        self.episodes = [Episode(i, content_id, self.n) for i in data.get('episodes')]

        self.watched = all(episode.watched for episode in self.episodes)

    def stamp(
        self
    ):
        if self.watched:
            return '{ico:check}'
        watched = sum(episode.watched for episode in self.episodes)
        if watched == 0:
            return None
        return f'{watched}/{len(self.episodes)}'

    def to_episode_pages(
        self,
        proxy: bool = False,
        alternative_player: bool = False
    ):
        items = []
        for episode in self.episodes:
            item = {
                'title': episode.menu_title(),
                'titleFooter': episode.footer(),
                'image': episode.thumbnail,
                'playerLabel': episode.player_title(),
                'action': episode.msx_action(
                    proxy=proxy,
                    alternative_player=alternative_player
                ),
                'focus': not episode.watched,
                'properties': episode.msx_properties(
                    proxy=proxy,
                    alternative_player=alternative_player
                )
            }
            progress = episode.progress()
            if progress is not None:
                item['progress'] = progress
            if episode.watched:
                item['stamp'] = '{ico:check}'
            items.append(item)

        return items
