import config


class MSX:

    def __init__(self):
        pass

    @staticmethod
    def start():
        return {
            'name': 'kino.pub',
            'version': '6.6.6',
            'parameter': f'menu:{config.MSX_HOST}/msx/menu?id={{ID}}',
            'welcome': 'none',
            'launcher': {
                "parameter": f'menu:{config.MSX_HOST}/msx/menu?id={{ID}}',
                "icon": "movie-filter",
                "image": "none",
                "color": "none"
            }
        }

    @staticmethod
    def unregistered_menu():
        return {
            "reuse": False,
            "cache": False,
            "restore": False,
            "headline": "kino.pub",
            "menu": [
                {
                    "icon": "vpn-key",
                    "label": "Регистрация",
                    "data": f"{config.MSX_HOST}/msx/registration?id={{ID}}"
                }
            ],
        }

    @staticmethod
    def registered_menu(categories):
        entry = {
            "reuse": False,
            "cache": False,
            "restore": False,
            "refocus": 1,
            "headline": "kino.pub",
            "menu": [category.to_msx() for category in categories or [] if not category.blacklisted],
        }
        entry['menu'].append({
            "type": "default",
            "label": "Мультфильмы",
            'data': f'request:interaction:{config.MSX_HOST}/msx/category?id={{ID}}&genre=23&page={{PAGE}}@{config.MSX_HOST}/paging.html'
        })
        entry['menu'].append({
            "type": "default",
            "label": "Аниме",
            'data': f'request:interaction:{config.MSX_HOST}/msx/category?id={{ID}}&genre=25&page={{PAGE}}@{config.MSX_HOST}/paging.html'
        })
        entry['menu'].append({
            "type": "default",
            "label": "Спорт",
            'data': f'{config.MSX_HOST}/msx/tv?id={{ID}}'
        })
        entry['menu'].append({
            "type": "default",
            "label": "Поиск",
            "icon": "search",
            'data': f'request:interaction:{config.MSX_HOST}/msx/search?id={{ID}}&q={{INPUT}}|search:3|ru@http://msx.benzac.de/interaction/input.html'
        })
        entry['menu'].append({
            "type": "default",
            "label": "Закладки",
            "icon": "bookmark",
            'data': f'{config.MSX_HOST}/msx/bookmarks?id={{ID}}'
        })
        entry['menu'].append({
            "type": "default",
            "label": "История",
            "icon": "history",
            'data': f"request:interaction:{config.MSX_HOST}/msx/history?id={{ID}}&page={{PAGE}}@{config.MSX_HOST}/paging.html"
        })
        entry['menu'].append({
            "type": "default",
            "label": "Я смотрю",
            "icon": "tv",
            'data': f'{config.MSX_HOST}/msx/watching?id={{ID}}'
        })
        return entry

    @staticmethod
    def already_registered():
        return {
            "type": "list",
            "headline": "Template",
            "template": {
                "type": "separate",
                "layout": "0,0,2,4",
                "color": "msx-glass",
                "title": "Title",
            },
            "items": [{
                "title": "Уже зарегистрирован"
            }]
        }

    @staticmethod
    def registration(user_code):
        return {
            "type": "pages",
            "headline": "Регистрация",
            "pages": [{
                "items": [
                    {
                        "type": "space",
                        "layout": "0,0,6,2",
                        "title": user_code,
                        "titleFooter": 'Используйте этот код для добавления устройства на kino.pub или зеркале, после ввода кода нажмите кнопку "Я ввел код".'
                    },
                    {
                        "type": "button",
                        "layout": "0,2,6,1",
                        "label": "Я ввёл код",
                        "action": f"execute:{config.MSX_HOST}/msx/check_registration?id={{ID}}"
                    }]
            }]
        }

    @staticmethod
    def code_not_entered():
        return {
            'response': {
                'status': 200,
                'data': {'action': 'warn:Код не введён'}
            }
        }

    @staticmethod
    def restart():
        return {
            'response': {
                'status': 200,
                'data': {'action': 'reload'}
            }
        }

    @staticmethod
    def content(entries, category, page, extra=None, decompress=None):
        resp = {
            "type": "list",
            "template": {
                "type": "separate",
                "layout": "0,0,2,4",
                "color": "msx-glass",
                "title": "Title"
            },
            "items": []
        }

        if decompress is not None:
            resp['template']['decompress'] = decompress

        if page == 1 and extra is None:
            resp['header'] = {
                "items": [
                    {
                        'type': 'button',
                        "layout": "0,0,3,1",
                        'label': 'Свежие',
                        'action': f'content:request:interaction:{config.MSX_HOST}/msx/category?id={{ID}}&category={category}&extra=fresh&page={{PAGE}}@{config.MSX_HOST}/paging.html'
                    },
                    {
                        'type': 'button',
                        "layout": "3,0,3,1",
                        'label': 'Горячие',
                        'action': f'content:request:interaction:{config.MSX_HOST}/msx/category?id={{ID}}&category={category}&extra=hot&page={{PAGE}}@{config.MSX_HOST}/paging.html'
                    },
                    {
                        'type': 'button',
                        "layout": "6,0,3,1",
                        'label': 'Популярные',
                        'action': f'content:request:interaction:{config.MSX_HOST}/msx/category?id={{ID}}&category={category}&extra=popular&page={{PAGE}}@{config.MSX_HOST}/paging.html'
                    },
                    {
                        'type': 'button',
                        "layout": "9,0,3,1",
                        'label': 'Жанры',
                        'action': f'content:{config.MSX_HOST}/msx/genres?id={{ID}}&category={category}'
                    }
                ]
            }
        for entry in entries:
            resp['items'].append(entry.to_msx())

        return resp

    @staticmethod
    def bookmark_folders(result):
        return {
            "type": "list",
            "headline": "Закладки",
            "template": {
                "type": "separate",
                "layout": "0,0,4,1",
                "color": "msx-glass",
            },
            "items": [i.to_msx() for i in result]
        }

    @staticmethod
    def genre_folders(category, result):
        return {
            "type": "list",
            "headline": "Жанры",
            "template": {
                "type": "separate",
                "layout": "0,0,4,1",
                "color": "msx-glass",
            },
            "items": [i.to_msx(category) for i in result]
        }

    @classmethod
    def update_panel(cls, content_id, value):
        return {
            'response': {
                'status': 200,
                'data': {
                    'action': f'update:panel:{content_id}',
                    'data': value
                }
            }
        }

    @classmethod
    def empty_response(cls):
        return {
            'response': {
                'status': 200,
                'data': {'action': '[]'}
            }
        }

    @classmethod
    def tv_channels(cls, channels):
        resp = {
            "type": "list",
            'header': {
                'items': [
                    {
                        'type': 'default',
                        'layout': '0,0,12,1',
                        "color": "msx-glass",
                        'headline': 'Спортивные каналы предоставляются в качестве бонуса и работают «как есть»',
                        'titleFooter': 'Для просмотра полноценного онлайн-ТВ с архивом рекомендуется использовать другие сервисы',
                        'action': '[]'
                    }
                ]
            },
            "template": {
                "type": "separate",
                "layout": "0,0,2,3",
                "color": "msx-glass",
                "title": "Title",
                "properties": {
                    'control:type': 'extended',
                    "button:content:enable": "false",
                    'button:restart:icon': 'settings',
                    'button:restart:action': MSX.player_action_btn(),
                    'progress:display': 'false'
                }
            },
            "items": [channel.to_msx() for channel in channels]
        }

        return resp

    @staticmethod
    def handle_exception(error_page=False):
        msg = {
            "type": "space",
            "layout": "0,0,6,2",
            "title": 'Произошла ошибка загрузки',
            "titleFooter": 'Скорее всего, кинопаб сейчас недоступен. Проверьте статус на kinopub.online и ожидайте ремонта.'
        }
        restart_app_btn = {
            "type": "button",
            "layout": "0,2,6,1",
            "label": "Перезапустить приложение",
            "action": f"reload"
        }
        reload_content_btn = {
            "type": "button",
            "layout": "0,3,6,1",
            "label": "Перезагрузить раздел",
            "action": f"reload:content"
        }
        reload_panel_btn = {
            "type": "button",
            "layout": "0,4,6,1",
            "label": "Перезагрузить окно",
            "action": f"reload:panel"
        }

        if error_page:
            items = [msg, restart_app_btn]
        else:
            items = [msg, restart_app_btn, reload_content_btn, reload_panel_btn]

        return {
            "menu": [{
                "label": "¯\\_(ツ)_/¯",
                "data": f"{config.MSX_HOST}/msx/error?id={{ID}}"
            }],
            "type": "pages",
            "headline": "Ошибка",
            "pages": [
                {
                    "items": items
                }
            ]
        }

    @staticmethod
    def unsupported_version():
        return {
            "menu": [{
                "label": "¯\\_(ツ)_/¯",
                "data": f"{config.MSX_HOST}/msx/too_old?id={{ID}}"
            }],
            "type": "pages",
            "headline": "Ошибка",
            "pages": [
                {
                    "items": [
                        {
                            "type": "space",
                            "layout": "0,0,6,2",
                            "title": 'Старая версия MSX',
                            "titleFooter": 'Используемая версия MSX слишком старая. Выберите один из параметров ниже для обновления. При выборе версии web.msx.benzac.de используйте вариант HTTPS. После обновления настройте кинопаб снова.'
                        }, {
                            "type": "button",
                            "layout": "0,2,6,1",
                            "label": "Параметр id:web",
                            "action": f"start",
                            "data": {
                                "name": "id:web",
                                "version": "2.0.3",
                                "parameter": "content:https://msx.benzac.de/services/web.php"
                            }
                        }, {
                            "type": "button",
                            "layout": "0,3,6,1",
                            "label": "Параметр web.msx.benzac.de",
                            "action": f"start",
                            "data": {
                                'name': 'web.msx.benzac.de',
                                'version': '1.0.2',
                                'parameter': "content:http://web.msx.benzac.de/msx/start.json",
                            }
                        }
                    ]
                }
            ]
        }

    @staticmethod
    def player_action_btn():
        if config.TIZEN:
            return 'content:request:interaction:init@https://msx.benzac.de/interaction/tizen.html'
        else:
            return 'panel:request:player:options'