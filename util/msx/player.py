from urllib.parse import urlencode

from config.settings import server
from util.proxy import make_proxy_url, remember_url


def player_action_btn():
    return 'panel:request:player:options'


def play_action(
    video_url,
    proxy: bool = False,
    alternative_player: bool = False,
    content_id=None,
    season=None,
    episode=None,
    position=None
):
    url = make_proxy_url(video_url) if proxy else video_url
    # Remember the CDN domain for the domains file regardless of whether the
    # stream itself is proxied.
    remember_url(video_url)
    if alternative_player:
        # Self-hosted copy of the html5x plugin with proper track names.
        player_url = f'{server.base_url}/html5x.html'
    else:
        # Self-hosted copy of the hlsx plugin (patched track indicators).
        player_url = f'{server.base_url}/hlsx.html'

    params = {'url': url}
    if content_id is not None:
        params['content_id'] = content_id
    if season is not None:
        params['season'] = season
    if episode is not None:
        params['episode'] = episode
    if position is not None and position > 0:
        params['position'] = int(position)

    return (
        f'video:plugin:{player_url}?'
        + urlencode(params)
        + '&client_id={ID}'
    )
