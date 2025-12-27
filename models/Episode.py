from urllib.parse import urlencode

import config
from util import msx
from util.proxy import make_proxy_url


class Episode:

    # TODO: Merge with Content?

    def __init__(self, data, content_id, season):
        self.content_id = content_id
        self.season = season

        self.n = data.get('number')
        self.title = data.get('title')

        self.watched = data.get('watched') == 1

        self.subtitle_tracks = {}

        video_files = None
        if config.QUALITY is not None:
            video_files = [i for i in data['files'] if i['quality'] == config.QUALITY]
            if len(video_files) == 0:
                video_files = None
            else:
                video_files = video_files[0]

        if video_files is None:
            video_files = sorted(data['files'], key=lambda x: x.get('quality_id'))[-1]

        self.video = video_files['url'][config.PROTOCOL]

        if config.PROTOCOL == 'http':
            for subtitle_track in data['subtitles']:
                language = subtitle_track.get('lang')
                self.subtitle_tracks[f'html5x:subtitle:{language}:{language}'] = subtitle_track['url']

    def menu_title(self):
        result = f'{self.n}. {self.title}'
        return result

    def player_title(self):
        return f'[S{self.season}/E{self.n}] {self.title}'

    def msx_action(self, proxy: bool = False):
        if proxy:
            url = make_proxy_url(self.video)
        else:
            url = self.video

        if config.TIZEN:
            return f'video:{url}'
        else:
            return f"video:plugin:{config.PLAYER}?" + urlencode({'url': url})

    def trigger_ready(self):
        params = {
            'content_id': self.content_id,
            'season': self.season,
            'episode': self.n
        }
        return msx.format_action('/msx/play', params=params, module='execute')
        #return f'execute:{config.MSX_HOST}/msx/play?{urlencode(params)}&id={{ID}}'


