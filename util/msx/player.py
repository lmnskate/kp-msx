from urllib.parse import urlencode, urlparse

from config.settings import server
from util.proxy import make_proxy_url, remember_domain


def player_action_btn():
    return 'panel:request:player:options'


def play_action(
    video_url,
    proxy: bool = False,
    alternative_player: bool = False
):
    url = make_proxy_url(video_url) if proxy else video_url
    if alternative_player:
        # Self-hosted copy of the html5x plugin with proper track names.
        # The plugin loads the master playlist through /msx/proxy when a
        # direct fetch fails (CORS), so the domain must be allowlisted.
        remember_domain(urlparse(video_url).netloc)
        player_url = f'{server.base_url}/html5x.html'
    else:
        # Self-hosted copy of the hlsx plugin (patched track indicators).
        player_url = f'{server.base_url}/hlsx.html'

    return f'video:plugin:{player_url}?' + urlencode({'url': url})
