from urllib.parse import urlencode

import config
from models.SubtitleTrack import SubtitleTrack
from util.proxy import remember_domain, make_proxy_url

class Video:

    def __init__(self, data):
        self.title = data.get('title')

        video_files = None
        if config.QUALITY is not None:
            video_files = [i for i in data.get('files', []) if i['quality'] == config.QUALITY]
            if len(video_files) == 0:
                video_files = None
            else:
                video_files = video_files[0]

        if video_files is None:
            video_files = sorted(data.get('files', []), key=lambda x: x.get('quality_id'))[-1]

        self.video = video_files['url'][config.PROTOCOL]

        self.subtitles = []
        for subtitle_track in data.get('subtitles', []):
            self.subtitles.append(SubtitleTrack(subtitle_track))

    def to_multivideo_entry(self, proxy: bool = False, alternative_player: bool = False):
        entry = {
            "label": self.title,
            'action': self.msx_action(proxy=proxy, alternative_player=alternative_player)
        }
        return entry

    def msx_action(self, proxy: bool = False, alternative_player : bool = False):
        if proxy:
            url = make_proxy_url(self.video)
        else:
            url = self.video

        if alternative_player:
            player = config.ALTERNATIVE_PLAYER
        else:
            player = config.PLAYER

        if config.TIZEN:
            return f'video:{url}'
        else:
            return f"video:plugin:{player}?" + urlencode({'url': url})

