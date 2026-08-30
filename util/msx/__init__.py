"""Builders for MSX JSON structures (menus, panels, players, error pages).

Split by topic; everything is re-exported here so consumers can keep using
`from util import msx` and `msx.<name>()`.
"""

from util.msx.core import (DEFAULT_PLAY_BUTTON_PROPS, POSTER_TEMPLATE,
                           build_list, does_not_exist, empty_history_response,
                           empty_response, empty_search_response,
                           format_action, handle_exception, icon, restart,
                           sad_screen, unsupported_version, update_panel)
from util.msx.menu import (bookmark_folders, build_categories, collections,
                           content_list, country_list, genre_folders,
                           registered_menu, start, tv_channels,
                           unregistered_menu)
from util.msx.player import play_action, player_action_btn
from util.msx.registration import (already_registered, code_image,
                                   code_not_entered, registration)
from util.msx.settings import (label, menu_entries_settings_panel,
                               poster_settings_panel, settings_button,
                               settings_menu, settings_screen, stamp, switch)
