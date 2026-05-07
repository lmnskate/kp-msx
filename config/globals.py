import aiohttp

# KinoPub API
BASE_URL = 'https://api.service-kp.com/v1'
OAUTH_URL = 'https://api.service-kp.com/oauth2/device'
TIMEOUT = aiohttp.ClientTimeout(total=15)

# KinoPub device setting keys
FOURK_SETTING = 'support4k'
HEVC_SETTING = 'supportHevc'
HDR_SETTING = 'supportHdr'
MIXED_PLAYLIST_SETTING = 'mixedPlaylist'
SERVER_LOCATION_SETTING = 'serverLocation'

# MSX text icons
LENNY = '¯\\_(ツ)_/¯'
SAD_LENNY = '(◡︵◡)'

# MSX settings UI element IDs
FOURK_ID = 'fourk'
HDR_ID = 'hdr'
HEVC_ID = 'hevc'
MIXED_PLAYLIST_ID = 'mixed_playlist'
SERVER_ID = 'server'
PROXY_ID = 'proxy'
ALTERNATIVE_PLAYER_ID = 'alternative_player'
SMALL_POSTERS_ID = 'small_posters'
MENU_ID = 'menu'
HELP_ID = 'help'

# MSX content button IDs
SUBSCRIPTION_BUTTON_ID = 'subscription_button'
BOOKMARK_BUTTON_ID = 'bookmark_button'
WATCH_BUTTON_ID = 'watch_button'
TRAILER_BUTTON_ID = 'trailer_button'

# Default video quality
DEFAULT_QUALITY = '1080p'

# Player URLs
#PLAYER_URL = 'https://slonopot.github.io/msx-hlsx/hlsx.html'
PLAYER_URL = 'http://192.168.2.90/msx-hlsx/hlsx.html'
ALTERNATIVE_PLAYER_URL = 'http://msx.benzac.de/plugins/html5x.html'
