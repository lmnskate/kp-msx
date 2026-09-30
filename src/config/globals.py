import aiohttp

# KinoPub API
BASE_URL = 'https://api.service-kp.com/v1'
OAUTH_URL = 'https://api.service-kp.com/oauth2/device'
TIMEOUT = aiohttp.ClientTimeout(total=15)

# KinoPub device setting keys
UHD_SETTING = 'support4k'
HEVC_SETTING = 'supportHevc'
HDR_SETTING = 'supportHdr'

# Preferred stream protocols in fallback order
PROTOCOL_PRIORITY = ['hls4', 'hls2', 'hls', 'http']

# Known quality labels ordered by ascending resolution
QUALITY_ORDER = ['480p', '720p', '1080p', '2160p']

# MSX settings UI element IDs
UHD_ID = 'uhd'
HDR_ID = 'hdr'
HEVC_ID = 'hevc'
PROXY_ID = 'proxy'
ALTERNATIVE_PLAYER_ID = 'alternative_player'
MENU_ID = 'menu'

# Menu entries that cannot be disabled via the settings screen
PINNED_MENU_ENTRIES = frozenset(['search', 'bookmarks', 'history', 'settings'])

# Settings shown as toggle switches instead of check stamps
SWITCH_IDS = frozenset([UHD_ID, HDR_ID, HEVC_ID, ALTERNATIVE_PLAYER_ID])

# MSX content button IDs
SUBSCRIPTION_BUTTON_ID = 'subscription_button'
BOOKMARK_BUTTON_ID = 'bookmark_button'
WATCH_BUTTON_ID = 'watch_button'
