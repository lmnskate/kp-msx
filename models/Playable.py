import config.globals as g
from config.settings import kp
from models.SubtitleTrack import SubtitleTrack
from util import msx
from util.proxy import make_proxy_url, make_subtitle_url, remember_url


def _progress_pct(
    duration,
    watch_time,
    watched=False
):
    if (
        watched or not duration or not watch_time or watch_time >= duration
    ):
        return None

    return round(100 * watch_time / duration)


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
        return _progress_pct(
            self.duration,
            self.watch_time,
            self.watched
        )

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
    def _quality_rank(
        quality
    ):
        try:
            return g.QUALITY_ORDER.index(quality)
        except ValueError:
            return -1

    @staticmethod
    def _pick_video_url(
        file_entry
    ):
        urls = file_entry.get('url', {})
        if not urls:
            return None

        if urls.get(kp.protocol):
            return urls[kp.protocol]

        for protocol in g.PROTOCOL_PRIORITY:
            if urls.get(protocol):
                return urls[protocol]

        return None

    @staticmethod
    def extract_video_url(
        data
    ):
        files = [
            f for f in data.get('files', [])
            if f.get('url')
        ]
        if not files:
            return None

        target_rank = Playable._quality_rank(kp.quality)

        def quality_key(
            file_entry
        ):
            rank = Playable._quality_rank(file_entry.get('quality'))
            if rank < 0:
                # Unknown quality goes to the very end
                return (2, 0)
            if rank <= target_rank:
                # Closest quality not above the target
                return (0, target_rank - rank)
            # Above the target, prefer the closest one
            return (1, rank - target_rank)

        def sort_key(
            file_entry
        ):
            q_group, q_distance = quality_key(file_entry)
            has_target = bool(
                (file_entry.get('url') or {}).get(kp.protocol)
            )
            try:
                protocol_index = g.PROTOCOL_PRIORITY.index(kp.protocol)
            except ValueError:
                protocol_index = 0
            # Within the same quality group prefer the target protocol,
            # then fallback to the priority list
            return (
                q_group,
                q_distance,
                0 if has_target else 1,
                protocol_index
            )

        files = sorted(files, key=sort_key)
        return Playable._pick_video_url(files[0])

    def _video_number(
        self
    ):
        return getattr(self, 'n', 1) or 1

    def _season_number(
        self
    ):
        return getattr(self, 'season', None)

    def _trigger_complete(
        self
    ):
        params = {'content_id': self.content_id, 'status': 'complete'}
        season = self._season_number()
        if season is not None:
            params['season'] = season
        params['episode'] = self._video_number()

        return msx.format_action(
            '/msx/play',
            params=params,
            module='execute'
        )

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
            alternative_player=alternative_player,
            content_id=self.content_id,
            season=self._season_number(),
            episode=self._video_number(),
            position=self.watch_time if not self.watched else None
        )

    def msx_properties(
        self,
        proxy: bool = False,
        alternative_player: bool = False
    ):
        props = {
            'resume:key': self.resume_key(),
            'trigger:complete': self._trigger_complete()
        }

        if not self.watched and self.watch_time and self.watch_time > 0:
            props['resume:position'] = str(self.watch_time)

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
