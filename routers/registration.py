from fastapi import APIRouter
from starlette.requests import Request

from models.KinoPub import KinoPub
from util import msx

router = APIRouter(prefix='/msx')


@router.get('/registration')
async def registration(request: Request):
    if request.state.device.registered():
        return msx.already_registered()
    user_code, device_code = await KinoPub.get_codes()
    request.state.device.update_code(device_code)
    return msx.registration(user_code)


@router.post('/check_registration')
async def check_registration(request: Request):
    result = await KinoPub.check_registration(request.state.device.code)
    if result is None:
        return msx.code_not_entered()
    request.state.device.update_tokens(result['access_token'], result['refresh_token'])
    await request.state.device.notify()
    return msx.restart()
