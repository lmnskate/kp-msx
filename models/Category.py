import config
from util import msx


class Category:

    BLACKLIST = ['4k']

    STATIC_CATEGORIES = [
        {'id': 'toons', 'title': 'Мультфильмы', 'path': '/msx/category', 'params': {'genre': '23', 'page': '{PAGE}'}, 'interaction': f'{config.MSX_HOST}/paging.html'},
        {'id': 'anime', 'title': 'Аниме', 'path': '/msx/category', 'params': {'genre': '25', 'page': '{PAGE}'}, 'interaction': f'{config.MSX_HOST}/paging.html'},
        {'id': 'sport', 'title': 'Спорт', 'path': '/msx/tv'},
        {'id': 'search', 'title': 'Поиск', 'icon': 'search', 'path': '/msx/search', 'params': {'q': '{INPUT}'}, 'interaction': 'http://msx.benzac.de/interaction/input.html', 'options': 'search:3|ru'},
        {'id': 'bookmarks', 'title': 'Закладки', 'icon': 'bookmark', 'path': '/msx/bookmarks'},
        {'id': 'history', 'title': 'История', 'icon': 'history', 'path': '/msx/history', 'params': {'page': '{PAGE}'}, 'interaction': f'{config.MSX_HOST}/paging.html'},
        {'id': 'watching', 'title': 'Я смотрю', 'icon': 'tv', 'path': '/msx/watching'}
    ]

    def __init__(self, data, blacklisted : bool = False):
        self.id = data.get('id')
        self.title = data.get('title')
        self.blacklisted = self.id in Category.BLACKLIST or blacklisted

        self.path = data.get('path')
        self.icon = data.get('icon')
        self.params = {}
        self.interaction = None
        self.options = None

        if self.path is None:
            # Built-in category
            self.path = '/msx/category'
            self.params = {'category': self.id, 'page': '{PAGE}'}
            self.interaction = f'{config.MSX_HOST}/paging.html'
        else:
            # Custom category
            self.params = data.get('params', {})
            self.interaction = data.get('interaction')
            self.options = data.get('options')

    def to_msx(self):
        return {
            "type": "default",
            "label": self.title,
            "icon": self.icon,
            "data": msx.format_action(self.path, params=self.params, interaction=self.interaction, options=self.options)
            #"data": f"{config.MSX_HOST}/msx/category?id={{ID}}&category={self.id}&page={{PAGE}}@{config.MSX_HOST}/paging.html"
        }

    @classmethod
    def static_categories(cls):
        return [cls(i) for i in Category.STATIC_CATEGORIES]
