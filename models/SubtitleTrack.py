class SubtitleTrack:
    def __init__(self, data):
        self.lang = data.get('lang', '?')
        self.url = data.get('url')
