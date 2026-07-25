from urllib.parse import urlencode

from config.settings import server
from util.msx.core import format_action, icon


def already_registered():
    return {
        'type': 'pages',
        'headline': 'Регистрация',
        'pages': [
            {
                'items': [
                    {
                        'type': 'space',
                        'layout': '0,0,12,5',
                        'color': 'msx-glass',
                        'alignment': 'center',
                        'headline': 'Уже зарегистрирован',
                        'text': 'Это устройство уже привязано к аккаунту Kinopub'
                    },
                    {
                        'type': 'button',
                        'layout': '0,5,12,1',
                        'enumerate': False,
                        'label': 'Перезапустить приложение',
                        'action': 'reload'
                    }
                ]
            }
        ]
    }


def code_image(user_code):
    return f'{server.base_url}/msx/registration/code_image?{urlencode({"code": user_code})}'


def registration(user_code):
    return {
        'type': 'pages',
        'headline': 'Регистрация',
        'pages': [
            {
                'items': [
                    {
                        'type': 'space',
                        'layout': '0,0,12,5',
                        'color': 'msx-glass',
                        'image': code_image(user_code),
                        'imageFiller': 'fit',
                        'imageOverlay': 0
                    },
                    {
                        'type': 'button',
                        'layout': '0,5,12,1',
                        'enumerate': False,
                        'label': 'Проверить код',
                        'action': format_action(
                            '/msx/check_registration', module='execute'
                        )
                    }
                ]
            }
        ]
    }


def code_not_entered():
    return {
        'response': {
            'status': 200,
            'data': {
                'action': 'warn:Код не введён. Если прошло больше 5 минут, перезапустите приложение для получения нового кода.'
            }
        }
    }
