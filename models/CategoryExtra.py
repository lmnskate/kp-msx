from config.settings import server
from util import msx


class CategoryExtra:
    EXTRAS = [
        lambda: {
            'title': 'Свежие',
            'layout': '0,0,3,1',
            'path': '/msx/category',
            'params': {
                'extra': 'fresh',
                'page': '{PAGE}'
            },
            'interaction': f'{server.host}/paging.html'
        },
        lambda: {
            'title': 'Горячие',
            'layout': '3,0,3,1',
            'path': '/msx/category',
            'params': {
                'extra': 'hot',
                'page': '{PAGE}'
            },
            'interaction': f'{server.host}/paging.html'
        },
        lambda: {
            'title': 'Популярные',
            'layout': '6,0,3,1',
            'path': '/msx/category',
            'params': {
                'extra': 'popular',
                'page': '{PAGE}'
            },
            'interaction': f'{server.host}/paging.html'
        },
        lambda: {
            'title': 'Жанры',
            'layout': '9,0,3,1',
            'path': '/msx/genres'
        }
    ]

    def __init__(self, data):
        self.title = data.get('title')
        self.path = data.get('path')
        self.params = data.get('params', {})
        self.interaction = data.get('interaction')
        self.layout = data.get('layout')

    def to_msx(self, category):
        params = {**self.params, 'category': category}

        return {
            'type': 'button',
            'layout': self.layout,
            'label': self.title,
            'action': msx.format_action(
                path=self.path,
                params=params,
                interaction=self.interaction,
                module='content'
            )
        }

    @classmethod
    def static_extras(cls):
        return [cls(i()) for i in CategoryExtra.EXTRAS]
