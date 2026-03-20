from config.globals import DEFAULT_QUALITY
from config.settings import kp
from models.SubtitleTrack import SubtitleTrack
from util import msx
from util.proxy import make_proxy_url


class Playable:
    def __init__(self, data):
        self.title = data.get('title')
        self.video_url = Playable.extract_video_url(data)
        self.subtitles = [SubtitleTrack(s) for s in data.get('subtitles', [])]

    @staticmethod
    def extract_video_url(data):
        files = data.get('files', [])
        best_file = None

        matches = [f for f in files if f.get('quality') == DEFAULT_QUALITY]
        if matches:
            best_file = matches[0]
        elif files:
            best_file = sorted(files, key=lambda x: x.get('quality_id'))[-1]

        if best_file:
            return best_file['url'][kp.protocol]
        return None

    def msx_action(
        self,
        proxy: bool = False,
        alternative_player: bool = False
    ):
        if not self.video_url:
            return 'warn:Почему-то нет видео'

        return msx.play_action(
            self.video_url,
            proxy=proxy,
            alternative_player=alternative_player
        )

    def msx_properties(
        self,
        proxy: bool = False,
        alternative_player: bool = False
    ):
        props = {
            'resume:key': self.resume_key(),
            'trigger:ready': self.trigger_ready()
        }

        props.update(msx.DEFAULT_PLAY_BUTTON_PROPS)

        subtitle_prefix = 'html5x' if alternative_player else 'hlsjs'
        for track in self.subtitles:
            props[f'{subtitle_prefix}:subtitle:{track.lang}:{track.lang.upper()}'] = (
                track.url if not proxy else make_proxy_url(track.url)
            )

        return props
