import re
from xml.sax.saxutils import escape

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response

from models.KinoPub import KinoPub
from util import msx

router = APIRouter(
    prefix='/msx'
)

CODE_PATTERN = re.compile(r'^[0-9A-Za-z-]{1,16}$')

CODE_IMAGE_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 480">
    <text x="600" y="270" text-anchor="middle" font-family="Roboto, Arial, sans-serif" font-size="240" font-weight="bold" fill="#ffffff" textLength="1000" lengthAdjust="spacingAndGlyphs">{code}</text>
    <text x="600" y="410" text-anchor="middle" font-family="Roboto, Arial, sans-serif" font-size="46" fill="#b3b3b3">Используйте этот код для активации устройства</text>
</svg>'''


@router.get('/registration/code_image')
async def registration_code_image(
    code: str
):
    if not CODE_PATTERN.match(code):
        return Response(status_code=400)

    svg = CODE_IMAGE_TEMPLATE.format(code=escape(code))

    return Response(
        svg,
        media_type='image/svg+xml'
    )


@router.get('/registration')
async def registration(
    request: Request
):
    if request.state.device.registered():
        return msx.already_registered()

    registration_codes = await KinoPub.get_codes()
    if registration_codes is None:
        return msx.handle_exception()

    user_code, device_code = registration_codes
    request.state.device.update_code(device_code)

    return msx.registration(user_code)


@router.post('/check_registration')
async def check_registration(
    request: Request
):
    result = await KinoPub.check_registration(request.state.device.code)
    if result is None:
        return msx.code_not_entered()

    request.state.device.update_tokens(
        result['access_token'],
        result['refresh_token']
    )
    await request.state.device.notify()

    return msx.restart()
