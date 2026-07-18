class Poster:
    SIZES = ['big', 'medium', 'small']
    PROXIES = [
        {'id': 'direct', 'title': 'Напрямую', 'template': '{url}'},
        {
            'id': 'phantom',
            'title': 'Phantom',
            'template': 'https://api.phantom.app/image-proxy/?image={url}&width=100'
        },
        {
            'id': 'magiceden',
            'title': 'Magic Eden',
            'template': 'https://img-cdn.magiceden.dev/rs:fill:200:0:0/plain/{url}'
        },
        {
            'id': 'wsrv',
            'title': 'wsrv.nl',
            'template': 'https://images.weserv.nl/?url={url}'
        },
    ]

    def __init__(self, data):
        self.big = data.get('big')
        self.medium = data.get('medium')
        self.small = data.get('small')
        self.wide = data.get('wide')

    def get(self, device_settings=None):
        if device_settings is None:
            poster_size = None
            poster_proxy = None
        else:
            poster_size = device_settings.poster_size
            poster_proxy = device_settings.poster_proxy

        poster_url = getattr(self, poster_size, None) or self.big
        return self._proxy_by_id(poster_proxy)['template'].format(url=poster_url)

    def get_wide(self, device_settings=None):
        if not self.wide:
            return None
        proxy = device_settings.poster_proxy if device_settings else None
        return self._proxy_by_id(proxy)['template'].format(url=self.wide)

    def format(self, size, proxy):
        url = getattr(self, size, None) or self.big
        return self._proxy_by_id(proxy)['template'].format(url=url)

    def _proxy_by_id(self, proxy_id):
        for proxy in self.PROXIES:
            if proxy['id'] == proxy_id:
                return proxy
        return self.PROXIES[0]
