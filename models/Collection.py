from util import msx, hacks


class Collection:

    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.poster = (data.get('posters') or {}).get('big')
        self.small_poster = hacks.posters_fix((data.get('posters') or {}).get('small'))

    def to_msx(self, small_poster: bool = False):
        return {
            'title': self.title,
            'truncation': 'title',
            'image': self.small_poster if small_poster else self.poster,
            'action': msx.format_action('/msx/collection', params={'collection_id': self.id}, module='content')
        }
