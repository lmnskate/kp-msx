from models.Episode import Episode



class Season:

    def __init__(self, data, content_id):
        self.content_id = content_id

        self.n = data.get('number')
        self.id = data.get('id')
        self.episodes = [Episode(i, content_id, self.n) for i in data.get('episodes')]

        self.watched = self._watched()

    def to_episode_pages(self, proxy: bool = False):
        items = []
        for i, episode in enumerate(self.episodes):
            entry = {
                "label": episode.menu_title(),
                "playerLabel": episode.player_title(),
                'action': episode.msx_action(proxy=proxy),
                'stamp': '{ico:check}' if episode.watched else None,
                'resumeKey': str(self.content_id) + ' ' + episode.player_title(),
                'triggerReady': episode.trigger_ready(),
                'focus': not episode.watched
            }
            items.append(entry)
        return items

    def _watched(self):
        watched = True
        for episode in self.episodes:
            watched = watched and episode.watched
        return watched