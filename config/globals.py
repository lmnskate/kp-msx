import aiohttp

# KinoPub API
BASE_URL = 'https://api.service-kp.com/v1'
OAUTH_URL = 'https://api.service-kp.com/oauth2/device'
TIMEOUT = aiohttp.ClientTimeout(total=15)

# KinoPub device setting keys
UHD_SETTING = 'support4k'
HEVC_SETTING = 'supportHevc'
HDR_SETTING = 'supportHdr'
MIXED_PLAYLIST_SETTING = 'mixedPlaylist'
SERVER_LOCATION_SETTING = 'serverLocation'

# File with all CDN domains seen by the server (for domain-based routing);
# contains registrable domains only (second-level + TLD)
CDN_DOMAINS_FILE = 'cdn-domains.txt'

# Compound public suffixes accounted for when reducing hostnames to
# registrable domains for CDN_DOMAINS_FILE (not an exhaustive PSL)
COMPOUND_TLDS = frozenset([
    'ac.uk', 'co.uk', 'gov.uk', 'org.uk',
    'co.jp', 'or.jp',
    'co.kr', 'or.kr',
    'co.nz', 'org.nz',
    'com.au', 'net.au', 'org.au',
    'com.br', 'com.cn', 'net.cn', 'org.cn',
    'com.mx', 'com.ru', 'net.ru', 'org.ru', 'pp.ru',
    'com.sg', 'com.tr', 'co.in'
])

# MSX settings UI element IDs
UHD_ID = 'uhd'
HDR_ID = 'hdr'
HEVC_ID = 'hevc'
MIXED_PLAYLIST_ID = 'mixed_playlist'
SERVER_ID = 'server'
PROXY_ID = 'proxy'
ALTERNATIVE_PLAYER_ID = 'alternative_player'
POSTERS_ID = 'posters'
MENU_ID = 'menu'
HELP_ID = 'help'
LOGOUT_ID = 'logout'

# Settings shown as toggle switches instead of check stamps
SWITCH_IDS = frozenset([UHD_ID, HDR_ID, HEVC_ID, ALTERNATIVE_PLAYER_ID])

# MSX content button IDs
SUBSCRIPTION_BUTTON_ID = 'subscription_button'
BOOKMARK_BUTTON_ID = 'bookmark_button'
WATCH_BUTTON_ID = 'watch_button'
TRAILER_BUTTON_ID = 'trailer_button'
SIMILAR_BUTTON_ID = 'similar_button'
CLEAR_HISTORY_BUTTON_ID = 'clear_history_button'
