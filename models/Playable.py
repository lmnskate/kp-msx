from config.settings import kp
from models.SubtitleTrack import SubtitleTrack
from util import msx
from util.proxy import make_proxy_url, make_subtitle_url, remember_url


class Playable:
    def __init__(
        self,
        data
    ):
        self.title = data.get('title')
        self.video_url = Playable.extract_video_url(data)
        self.subtitles = [SubtitleTrack(s) for s in data.get('subtitles', [])]
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')
        remember_url(self.thumbnail)
        watching = data.get('watching') or {}
        self.watch_time = watching.get('time') or 0
        self.watched = data.get('watched') == 1

    def progress(
        self
    ):
        if (
            self.watched
            or not self.duration
            or not self.watch_time
            or self.watch_time >= self.duration
        ):
            return None
        return round(100 * self.watch_time / self.duration)

    def footer(
        self
    ):
        parts = []
        if self.duration:
            parts.append(f'{self.duration // 60} мин')
        if not self.watched and self.duration and self.watch_time:
            left = self.duration - self.watch_time
            if left > 0:
                parts.append(f'осталось {left // 60} мин')

        return ' · '.join(parts) or None

    @staticmethod
    def extract_video_url(
        data
    ):
        files = data.get('files', [])
        best_file = None

        matches = [f for f in files if f.get('quality') == kp.quality]
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
        for index, track in enumerate(self.subtitles, start=1):
            remember_url(track.url)
            # Same style as the subtitle track names in the KinoPub HLS
            # manifest ("RUS #01", "ENG #02")
            label = f'{track.lang.upper()} #{index:02d}'

            if alternative_player:
                # The html5x player requires WebVTT, so subtitles are always
                # routed through the converting endpoint
                url = make_subtitle_url(track.url)
            elif proxy:
                url = make_proxy_url(track.url)
            else:
                url = track.url

            props[f'{subtitle_prefix}:subtitle:{track.lang}:{label}'] = url

        return props
