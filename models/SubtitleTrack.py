from util.proxy import make_proxy_url


class SubtitleTrack:

    def __init__(self, data):
        self.lang = data.get('lang', '?')
        self.url = data.get('url')

    def to_msx_properties(self, player: str = 'html5x', proxy: bool = False):
        if proxy:
            url = make_proxy_url(self.url)
        else:
            url = self.url
        return {f'{player}:subtitle:{self.lang}:{self.lang.upper()}': url}
