from models.Folder import Folder
from models.MSX import MSX
from models.Season import Season
from models.Video import Video


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

        self.watched = data.get('watched') == 1

        self.videos = None

        if (videos := data.get('videos')) is not None:
           self.videos = [Video(i) for i in videos]

        self.seasons = None

        if (seasons := data.get('seasons')) is not None:
            self.poster = (data.get('posters') or {}).get('big')
            self.seasons = [Season(i, self.id) for i in seasons]

        self.new_episodes = data.get('new')

    def update_bookmarks(self, folders):
        self.bookmarks = [i.id for i in folders]

    def to_msx(self):
        entry = {
            'title': self.title,
            'image': self.poster,
            "action": MSX.format_action('/msx/content', params={'content_id': self.id}, module='panel')
            #"action": f"panel:{config.MSX_HOST}/msx/content?id={{ID}}&content_id={self.id}"
        }
        if self.media is not None and self.media.season > 0:
            entry['titleFooter'] = self.media.to_subtitle()
        else:
            entry['titleFooter'] = ''
            if self.rating:
                entry['titleFooter'] += f' {{ico:stars}} {self.rating}'
            if self.year:
                entry['titleFooter'] += f' {{ico:calendar-month}} {self.year}'
            if self.new_episodes is not None:
                entry['titleFooter'] += f' {{ico:new-releases}} {self.new_episodes}'

            entry['titleFooter'] = entry['titleFooter'].strip()
        return entry

    def msx_action(self):
        if self.videos is not None:
            if len(self.videos) == 1:
                return self.videos[0].msx_action()
            else:
                return MSX.format_action('/msx/multivideo', params={'content_id': self.id}, module='panel')
                #return f'panel:{config.MSX_HOST}/msx/multivideo?id={{ID}}&content_id={self.id}'
        if self.seasons is not None:
            return MSX.format_action('/msx/seasons', params={'content_id': self.id}, module='panel')
            #return f"panel:{config.MSX_HOST}/msx/seasons?id={{ID}}&content_id={self.id}"

    SUBSCRIPTION_BUTTON_ID = "subscription_button"
    BOOKMARK_BUTTON_ID = "bookmark_button"
    WATCH_BUTTON_ID = "watch_button"

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
            'action': MSX.format_action('/msx/toggle_subscription', params={'content_id': self.id}, module='execute'),
            #'action': f'execute:{config.MSX_HOST}/msx/toggle_subscription?content_id={self.id}&id={{ID}}',
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
            'action': MSX.format_action('/msx/content/bookmarks', params={'content_id': self.id}, module='panel')
            #'action': f'panel:{config.MSX_HOST}/msx/content/bookmarks?id={{ID}}&content_id={self.id}'
        }

        return button

    def to_msx_panel(self):
        buttons = []

        if self.seasons:
            buttons.append(self.to_subscription_button())

        buttons.append(self.to_bookmark_button())

        watch_button = {
            "id": self.WATCH_BUTTON_ID,
            "type": "button",
            "layout": f"4,5,{4-len(buttons)},1",
            "label": "Смотреть",
            "playerLabel": self.title,
            'focus': True,
            'action': self.msx_action(),
            'properties': {
                'control:type': 'extended',
                'button:content:icon': 'list-alt',
                'button:content:action': f'player:content',
                'button:content:enable': f'false',
                'button:restart:icon': 'settings',
                'button:restart:action': MSX.player_action_btn(),
                'button:speed:icon': 'replay',
                'button:speed:action': 'player:restart',
                'resume:key': self.title,
                'trigger:ready': MSX.format_action('/msx/play', params={'content_id': self.id}, module='execute')
                #'trigger:ready': f'execute:{config.MSX_HOST}/msx/play?content_id={self.id}&id={{ID}}'
            }
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
                'stampColor': 'msx-glass',
            },
            "items": []
        }

        for season in self.seasons:
            entry['items'].append({
                "label": f"Cезон {season.n}",
                'stamp': '{ico:check}' if season.watched else None,
                'focus': not season.watched,
                "action": MSX.format_action('/msx/episodes', params={'content_id': self.id, 'season': season.n}, module='panel')
               #"action": f'panel:{config.MSX_HOST}/msx/episodes?id={{ID}}&content_id={self.id}&season={season.n}',
            })
        return entry

    def to_multivideo_msx_panel(self):
        entry = {
            "type": "list",
            "headline": self.title,
            'template': {
                'enumerate': False,
                "type": "button",
                "layout": f"0,0,8,1",
                'stampColor': 'msx-glass',
                'playerLabel': self.title,
                'properties': {
                    'control:type': 'extended',
                    'button:content:icon': 'list-alt',
                    'button:content:action': f'player:content',
                    'button:content:enable': f'false',
                    'button:restart:icon': 'settings',
                    'button:restart:action': MSX.player_action_btn(),
                    'button:speed:icon': 'replay',
                    'button:speed:action': 'player:restart',
                    'resume:key': self.title,
                    'trigger:ready': MSX.format_action('/msx/play', params={'content_id': self.id}, module='execute')
                    #'trigger:ready': f'execute:{config.MSX_HOST}/msx/play?content_id={self.id}&id={{ID}}'
                }
            },
            "items": [i.to_multivideo_entry() for i in self.videos]
        }
        return entry

    def to_episodes_msx_panel(self, season_number):
        for season in self.seasons:
            if season.n == season_number:
                break
        entry = {
            "type": "list",
            "headline": f'{self.title} [S{season.n}]',
            'template': {
                #'enumerate': False,  # breaks previous/next buttons in player
                "type": "button",
                "layout": f"0,0,8,1",
                'stampColor': 'msx-glass',
                'properties': {
                    'control:type': 'extended',
                    'button:content:icon': 'list-alt',
                    'button:content:action': f'player:content',
                    'button:restart:icon': 'settings',
                    'button:restart:action': MSX.player_action_btn(),
                    'button:speed:icon': 'replay',
                    'button:speed:action': 'player:restart',
                    'resume:key': '{context:resumeKey}',
                    'trigger:ready': '{context:triggerReady}'
                }
            },
            "items": season.to_episode_pages()
        }
        return entry

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
                "action": MSX.format_action('/msx/toggle_bookmark', params={'content_id': self.id, 'folder_id': folder.id}, module='execute')
                #"action": f'execute:{config.MSX_HOST}/msx/toggle_bookmark?content_id={self.id}&folder_id={folder.id}&id={{ID}}'
            }
            subentry.update(self.to_bookmark_stamp(folder.id))
            entry['items'].append(subentry)
        return entry

