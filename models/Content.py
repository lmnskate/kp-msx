import config
from models.Folder import Folder
from models.MSX import MSX
from models.Season import Season


class Content:

    def __init__(self, data, media=None):
        self.media = media

        self.id = data.get('id')
        self.title = data.get('title')
        self.type = data.get('type')
        self.plot = data.get('plot')
        self.voice = data.get('voice')
        self.cast = data.get('cast')
        self.year = data.get('year')
        self.subscribed = data.get('subscribed')

        if self.voice:
            self.plot += f'\n\nОзвучки: {self.voice}'
        if self.cast:
            self.plot += f'\n\nВ ролях: {self.cast}'

        self.poster = (data.get('posters') or {}).get('big')
        self.rating = data.get('imdb_rating') or data.get('kinopoinsk_rating')

        self.bookmarks = data.get('bookmarks')
        if self.bookmarks is not None and isinstance(self.bookmarks, list):
            self.bookmarks = [Folder(i).id for i in self.bookmarks]

        self.video = None

        self.watched = data.get('watched') == 1

        self.subtitle_tracks = dict()

        if (videos := data.get('videos')) is not None:
            video_entry = None

            for _video in videos:
                if len(_video['files']) > 0:
                    video_entry = _video
                    break

            video_files = None
            if config.QUALITY is not None:
                video_files = [i for i in video_entry['files'] if i['quality'] == config.QUALITY]
                if len(video_files) == 0:
                    video_files = None
                else:
                    video_files = video_files[0]

            if video_files is None:
                video_files = sorted(video_entry['files'], key=lambda x: x.get('quality_id'))[-1]

            self.video = video_files['url'][config.PROTOCOL]

            if config.PROTOCOL == 'http':
                for subtitle_track in video_entry['subtitles']:
                    language = subtitle_track.get('lang')
                    self.subtitle_tracks[f'html5x:subtitle:{language}:{language}'] = subtitle_track['url']

        self.seasons = None

        if (seasons := data.get('seasons')) is not None:
            self.poster = (data.get('posters') or {}).get('big')
            self.seasons = [Season(i, self.id) for i in seasons]

    def msx_path(self):
        return f'/content?id={{ID}}&content_id={self.id}'

    def to_msx(self):
        entry = {
            'title': self.title,
            'image': self.poster,
            "action": f"panel:{config.MSX_HOST}/msx/content?id={{ID}}&content_id={self.id}"
        }
        if self.media is not None and self.type == 'serial':
            entry['titleFooter'] = self.media.to_subtitle()
        else:
            entry['titleFooter'] = ''
            if self.rating:
                entry['titleFooter'] += f' {{ico:stars}} {self.rating}'
            if self.year:
                entry['titleFooter'] += f' {{ico:calendar-month}} {self.year}'
            entry['titleFooter'] = entry['titleFooter'].strip()
        return entry

    def msx_action(self):
        if self.video is not None:
            return f"[video:plugin:{config.PLAYER}?url={self.video}|execute:{config.MSX_HOST}/msx/play?content_id={self.id}&id={{ID}}]"
        if self.seasons is not None:
            return f"panel:{config.MSX_HOST}/msx/seasons?id={{ID}}&content_id={self.id}"

    SUBSCRIPTION_BUTTON_ID = "subscription_button"
    BOOKMARK_BUTTON_ID = "bookmark_button"

    def to_subscription_button(self):
        if self.subscribed:
            label = "{ico:msx-yellow:new-releases}"
        else:
            label = "{ico:msx-white:new-releases}"
        button = {
            "id": self.SUBSCRIPTION_BUTTON_ID,
            "type": "button",
            "layout": f"6,5,1,1",
            "label": label,
            'action': f'execute:{config.MSX_HOST}/msx/toggle_subscription?content_id={self.id}&id={{ID}}',
        }

        return button

    def to_bookmark_button(self):
        if self.in_bookmarks():
            label = "{ico:msx-yellow:bookmark}"
        else:
            label = "{ico:msx-white:bookmark}"

        button = {
            "id": self.BOOKMARK_BUTTON_ID,
            "type": "button",
            "layout": f"7,5,1,1",
            "label": label,
            'action': f'panel:{config.MSX_HOST}/msx/content/bookmarks?id={{ID}}&content_id={self.id}'
        }

        return button

    def to_msx_panel(self):
        buttons = []

        if self.seasons:
            buttons.append(self.to_subscription_button())

        buttons.append(self.to_bookmark_button())

        watch_button = {
            "type": "button",
            "layout": f"4,5,{4-len(buttons)},1",
            "label": "Смотреть",
            'focus': True,
            'action': self.msx_action(),
            # 'properties': self.subtitle_tracks
        }

        buttons = [watch_button] + buttons

        stamp = ''
        if self.rating:
            stamp += f' {{ico:stars}} {self.rating}'
        if self.year:
            stamp += f' {{ico:calendar-month}} {self.year}'
        stamp = stamp.strip()
        if len(stamp) == 0:
            stamp = None

        return {
            "type": "pages",
            "headline": self.title,
            "pages": [
                {
                    "items": [
                        {
                            "type": "teaser",
                            "layout": "0,0,4,6",
                            "image": self.poster,
                            "imageFiller": "height-left",
                            'action': 'focus:plot',
                            'stamp': stamp
                        },
                        {
                            "type": "default",
                            "layout": "4,0,4,5",
                            #"headline": self.title,
                            "text": self.plot,
                            'action': 'focus:plot'
                        }
                    ] + buttons
                }, {
                    'items': [
                        {
                            'id': 'plot',
                            "type": "default",
                            "layout": "0,0,8,6",
                            #"headline": self.title,
                            "text": self.plot,
                        }
                    ]
                }
            ]

        }

    def to_seasons_msx_panel(self):
        entry = {
            "type": "list",
            "headline": self.title,
            "template": {
                'enumerate': False,
                "type": "button",
                'layout': "0,0,2,1",
            },
            "items": []
        }
        for season in self.seasons:
            entry['items'].append({
                "label": f"Cезон {season.n}",
                "action": f'panel:{config.MSX_HOST}/msx/episodes?id={{ID}}&content_id={self.id}&season={season.n}'
            })
        return entry

    def to_episodes_msx_panel(self, season_number):
        for season in self.seasons:
            if season.n == season_number:
                break
        entry = {
            "type": "list",
            "headline": f'{self.title} [S{season.n}]',
            'template': {
                'enumerate': False,
                "type": "button",
                "layout": f"0,0,8,1",
                'stampColor': 'msx-glass'
            },
            "items": season.to_episode_pages()
        }
        return entry

    def to_player_opts(self, season=None, episode=None):
        acts = []
        if self.seasons is None:
            acts += MSX.player_update_title(self.title)
            #acts += MSX.player_commit(self.subtitle_tracks)
        else:
            for _season in self.seasons:
                if _season.n != int(season):
                    continue
                for _episode in _season.episodes:
                    if _episode.n == int(episode):
                        break
                break
            acts += _season.to_msx_player_update_actions(episode)
            acts += MSX.player_update_title(_episode.player_title())
            #acts += MSX.player_commit(_episode.subtitle_tracks)
        return acts

    def in_bookmarks(self):
        return self.bookmarks is not None and len(self.bookmarks) > 0

    def to_bookmark_stamp(self, folder_id):
        return {
            'stampColor': 'msx-glass' if folder_id in self.bookmarks else 'transparent',
            'stamp': '{ico:check}' if folder_id in self.bookmarks else '{ico:blank}'
        }

    def to_bookmarks_msx_panel(self, folders: 'list[Folder]'):
        entry = {
            "type": "list",
            "headline": 'Закладки',
            "template": {
                'enumerate': False,
                "type": "button",
                'layout': "0,0,4,1",
            },
            "items": []
        }
        for folder in folders:
            subentry = {
                "id": str(folder.id),
                "label": folder.title,
                "action": f'execute:{config.MSX_HOST}/msx/toggle_bookmark?content_id={self.id}&folder_id={folder.id}&id={{ID}}'
            }
            subentry.update(self.to_bookmark_stamp(folder.id))
            entry['items'].append(subentry)
        return entry

