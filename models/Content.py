from models.Folder import Folder
from models.Season import Season
from models.Video import Video
from util import hacks, msx


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
        self.imdb = data.get('imdb')

        if self.voice:
            self.plot += f'\n\nОзвучки: {self.voice}'
        if self.cast:
            self.plot += f'\n\nВ ролях: {self.cast}'

        self.poster = (data.get('posters') or {}).get('big')
        self.small_poster = hacks.posters_fix((data.get('posters') or {}).get('small'))

        self.rating = data.get('imdb_rating') or data.get('kinopoinsk_rating')
        self.is_4k = data.get('quality') == 2160

        bookmarks = data.get('bookmarks')
        self.bookmarks = (
            list(Folder(i).id for i in bookmarks)
            if isinstance(bookmarks, list)
            else bookmarks
        )

        self.watched = data.get('watched') == 1

        self.videos = None

        if (videos := data.get('videos')) is not None:
            self.videos = [Video(i, self.id, self.title) for i in videos]

        self.seasons = None

        if (seasons := data.get('seasons')) is not None:
            self.poster = (data.get('posters') or {}).get('big')
            self.seasons = [Season(i, self.id) for i in seasons]

        self.new_episodes = data.get('new')

        self.trailer = (data.get('trailer') or {}).get('url')

    def update_bookmarks(self, folders):
        self.bookmarks = [i.id for i in folders]

    def to_msx(self, small_poster: bool = False):
        entry = {
            'title': self.title,
            'image': self.small_poster if small_poster else self.poster,
            'action': msx.format_action(
                '/msx/content', params={'content_id': self.id}, module='panel',
            ),
        }

        if self.media is not None and self.media.season > 0:
            entry['titleFooter'] = self.media.to_subtitle()
        else:
            if self.year:
                entry['titleFooter'] = str(self.year)
            if self.rating:
                entry['tag'] = str(self.rating)
                entry['tagColor'] = 'msx-yellow'
            if self.is_4k:
                entry['badge'] = '4K'
                entry['badgeColor'] = 'msx-blue'
            if self.new_episodes is not None:
                entry['stamp'] = f'+{self.new_episodes}'
                entry['stampColor'] = 'msx-yellow'

        return entry

    def msx_action(self, proxy: bool = False, alternative_player: bool = False):
        if self.videos is not None:
            if len(self.videos) == 1:
                return self.videos[0].msx_action(
                    proxy=proxy, alternative_player=alternative_player,
                )
            else:
                return msx.format_action(
                    '/msx/multivideo', params={'content_id': self.id}, module='panel',
                )
        if self.seasons is not None:
            return msx.format_action(
                '/msx/seasons', params={'content_id': self.id}, module='panel'
            )

    SUBSCRIPTION_BUTTON_ID = 'subscription_button'
    BOOKMARK_BUTTON_ID = 'bookmark_button'
    WATCH_BUTTON_ID = 'watch_button'
    TRAILER_BUTTON_ID = 'trailer_button'

    def to_subscription_button(self):
        if self.subscribed:
            label = '{ico:msx-yellow:new-releases}'
        else:
            label = '{ico:msx-white:new-releases}'
        return {
            'id': self.SUBSCRIPTION_BUTTON_ID,
            'type': 'button',
            'layout': '6,5,1,1',
            'label': label,
            'action': msx.format_action(
                '/msx/toggle_subscription',
                params={'content_id': self.id},
                module='execute',
            ),
        }

    def to_bookmark_button(self):
        if self.in_bookmarks():
            label = '{ico:msx-yellow:bookmark}'
        else:
            label = '{ico:msx-white:bookmark}'
        return {
            'id': self.BOOKMARK_BUTTON_ID,
            'type': 'button',
            'layout': '7,5,1,1',
            'label': label,
            'action': msx.format_action(
                '/msx/content/bookmarks', params={'content_id': self.id}, module='panel',
            ),
        }

    def to_trailer_button(
        self, qty, proxy: bool = False, alternative_player: bool = False
    ):
        props = {'trigger:background': 'player:button:eject:execute'}
        props.update(msx.DEFAULT_PLAY_BUTTON_PROPS)
        return {
            'id': self.TRAILER_BUTTON_ID,
            'type': 'button',
            'layout': f'{7 - qty},5,1,1',
            'label': '{ico:msx-white:movie}',
            'playerLabel': f'Трейлер {self.title}',
            'properties': props,
            'action': msx.play_action(
                self.trailer, proxy=proxy, alternative_player=alternative_player
            ),
        }

    def to_msx_panel(
        self,
        proxy: bool = False,
        alternative_player: bool = False,
        small_poster: bool = False,
    ):
        buttons = [self.to_bookmark_button()]

        if self.seasons:
            buttons.append(self.to_subscription_button())

        if self.trailer:
            buttons.append(
                self.to_trailer_button(
                    len(buttons), proxy=proxy, alternative_player=alternative_player
                )
            )

        watch_button = {
            'id': self.WATCH_BUTTON_ID,
            'type': 'button',
            'layout': f'4,5,{4 - len(buttons)},1',
            'label': (
                'Смотреть'
                if len(buttons) <= 2
                else '{ico:msx-white:play-circle-outline}'
            ),
            'playerLabel': self.title,
            'focus': True,
            'action': self.msx_action(
                proxy=proxy, alternative_player=alternative_player
            ),
        }

        if self.videos is not None and len(self.videos) == 1:
            watch_button['properties'] = self.videos[0].msx_properties(
                proxy=proxy, alternative_player=alternative_player
            )

        buttons = [watch_button] + buttons

        teaser = {
            'id': 'teaser',
            'type': 'teaser',
            'layout': '0,0,4,6',
            'image': self.small_poster if small_poster else self.poster,
            'imageFiller': 'height-left',
            'imageOverlay': 2,
            'action': 'focus:plot',
        }
        if self.rating:
            teaser['badge'] = str(self.rating)
            teaser['badgeColor'] = 'msx-yellow'
        if self.year:
            teaser['tag'] = str(self.year)
            teaser['tagColor'] = 'msx-glass'
        if self.is_4k:
            teaser['stamp'] = '4K'
            teaser['stampColor'] = 'msx-blue'

        page_items = [
            teaser,
            {
                'type': 'default',
                'layout': '4,0,4,5',
                'text': self.plot,
                'action': 'focus:plot',
            },
        ]
        page_items.extend(buttons)

        return {
            'type': 'pages',
            'headline': self.title,
            'pages': [
                {
                    'items': page_items,
                },
                {
                    'items': [
                        {
                            'id': 'plot',
                            'type': 'default',
                            'layout': '0,0,8,6',
                            'text': self.plot,
                            'action': 'focus:teaser',
                        }
                    ],
                },
            ],
        }

    def to_seasons_msx_panel(self):
        return {
            'type': 'list',
            'headline': self.title,
            'template': {
                'enumerate': False,
                'type': 'button',
                'layout': '0,0,2,1',
                'stampColor': 'msx-glass',
            },
            'items': list(
                {
                    'label': f'Cезон {season.n}',
                    'stamp': '{ico:check}' if season.watched else None,
                    'focus': not season.watched,
                    'action': msx.format_action(
                        '/msx/episodes',
                        params={'content_id': self.id, 'season': season.n},
                        module='panel',
                    ),
                }
                for season in self.seasons
            ),
        }

    def to_multivideo_msx_panel(
        self, proxy: bool = False, alternative_player: bool = False
    ):
        return {
            'type': 'list',
            'headline': self.title,
            'template': {
                'enumerate': False,
                'type': 'button',
                'layout': '0,0,8,1',
                'stampColor': 'msx-glass',
                'playerLabel': self.title,
            },
            'items': [
                i.to_multivideo_entry(
                    proxy=proxy, alternative_player=alternative_player
                )
                for i in self.videos
            ],
        }

    def to_episodes_msx_panel(
        self, season_number, proxy: bool = False, alternative_player: bool = False,
    ):
        season = next(s for s in self.seasons if s.n == season_number)
        return {
            'type': 'list',
            'headline': f'{self.title} [S{season.n}]',
            'template': {
                'type': 'button',
                'layout': '0,0,8,1',
                'stampColor': 'msx-glass',
            },
            'items': season.to_episode_pages(
                proxy=proxy, alternative_player=alternative_player
            ),
        }

    def in_bookmarks(self):
        return self.bookmarks is not None and len(self.bookmarks) > 0

    def to_bookmark_stamp(self, folder_id):
        return msx.stamp(folder_id in self.bookmarks)

    def to_bookmarks_msx_panel(self, folders):
        return {
            'type': 'list',
            'headline': 'Закладки',
            'template': {
                'enumerate': False,
                'type': 'button',
                'layout': '0,0,4,1',
            },
            'items': list(
                {
                    'id': str(folder.id),
                    'label': folder.title,
                    'action': msx.format_action(
                        '/msx/toggle_bookmark',
                        params={'content_id': self.id, 'folder_id': folder.id},
                        module='execute',
                    ),
                    **self.to_bookmark_stamp(folder.id),
                }
                for folder in folders
            ),
        }
