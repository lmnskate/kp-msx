from util import msx


class Country:
    def __init__(
        self,
        data
    ):
        self.id = data.get('id')
        self.title = data.get('title')

    def to_msx(
        self,
        category
    ):
        return {
            'type': 'default',
            'label': self.title,
            'action': msx.format_action(
                '/msx/category',
                params={
                    'category': category,
                    'country': self.id,
                    'page': '{PAGE}'},
                interaction='/paging.html',
                module='content'
            )
        }
