from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import aiohttp

import config.globals as g
from config.settings import kp
from models.Category import Category
from models.Channel import Channel
from models.Collection import Collection
from models.Content import Content
from models.Folder import Folder
from models.Genre import Genre
from models.Media import Media
from models.Reference import Reference
from util import db

if TYPE_CHECKING:
    from models.Device import Device

logger = logging.getLogger(__name__)


class KinoPub:

    def __init__(self, token, refresh):
        self.token = token
        self.refresh = refresh
        self.session: aiohttp.ClientSession | None = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={'Authorization': f'Bearer {self.token}'},
                timeout=g.TIMEOUT
            )
        return self.session

    async def close_session(self) -> None:
        if self.session is not None and not self.session.closed:
            await self.session.close()
        self.session = None

    async def api(
        self,
        path,
        params=None,
        method='GET',
        retried=False
    ):
        session = await self.get_session()
        url = f'{g.BASE_URL}{path}'
        if method == 'GET':
            response = await session.get(url, params=params)
        else:
            response = await session.request(
                method,
                url,
                json=params
            )

        if response.status == 401 and not retried:
            reauth_result = await self.refresh_tokens()
            if reauth_result:
                return await self.api(
                    path,
                    params=params,
                    method=method,
                    retried=True
                )
            return None
        result = await response.json()
        return result

    async def fetch_list(
        self,
        path,
        model,
        key='items',
        params=None,
        default=None
    ):
        result = await self.api(path, params=params)
        if result is None:
            return default
        return [model(i) for i in result[key]]

    async def get_content_categories(self):
        return await self.fetch_list('/types', Category, default=[])

    async def get_genres(self, category=None):
        return await self.fetch_list(
            '/genres',
            Genre,
            params={'type': category},
            default=[]
        )

    async def get_content(
        self,
        category=None,
        page=1,
        extra=None,
        genre=None,
        sort=None
    ):
        path = f'/items/{extra}' if extra else '/items'
        params = {'page': page}
        if category:
            params['type'] = category
        if genre:
            params['genre'] = genre
        if sort:
            params['sort'] = sort
        return await self.fetch_list(
            path,
            Content,
            params=params,
            default=[]
        )

    async def search(self, query):
        return await self.fetch_list(
            '/items/search',
            Content,
            params={'q': query},
            default=[]
        )

    async def get_single_content(self, id):
        result = await self.api(f'/items/{id}')
        if result is None:
            return None
        return Content(result['item'])

    async def get_bookmark_folders(self):
        return await self.fetch_list('/bookmarks', Folder, default=[])

    async def create_bookmark_folder(self, name: str = 'Мои закладки'):
        await self.api(
            '/bookmarks/create',
            {'title': name},
            method='POST'
        )

    async def get_content_folders(self, content_id):
        return await self.fetch_list(
            '/bookmarks/get-item-folders',
            Folder,
            key='folders',
            params={'item': content_id},
            default=[]
        )

    async def get_bookmark_folder(self, folder_id, page=1):
        result = await self.api(f'/bookmarks/{folder_id}', {'page': page})
        if result is None:
            return []
        try:
            current_page = result['pagination']['current']
            if page > current_page:
                return []
        except (KeyError, TypeError):
            pass
        return [Content(i) for i in result['items']]

    async def get_history(self, page=1):
        result = await self.api('/history', {'page': page})
        if result is None:
            return []
        return [Content(i['item'], Media(i['media'])) for i in result['history']]

    async def get_watching(self, subscribed=0):
        return await self.fetch_list(
            '/watching/serials',
            Content,
            params={'subscribed': subscribed},
            default=[]
        )

    async def get_tv(self):
        return await self.fetch_list(
            '/tv',
            Channel,
            key='channels',
            default=[]
        )

    async def get_collections(self, page):
        return await self.fetch_list(
            '/collections',
            Collection,
            params={'page': page},
            default=[]
        )

    async def get_single_collection(self, collection_id):
        return await self.fetch_list(
            '/collections/view',
            Content,
            params={'id': collection_id},
            default=[]
        )

    async def notify(self, device_id):
        await self.api(
            '/device/notify',
            {
                'title': 'KP-MSX',
                'hardware': g.LENNY,
                'software': device_id
            },
            method='POST'
        )

    async def toggle_watched(
        self,
        content_id,
        season=None,
        episode=None
    ):
        params = {'id': content_id}
        if season is not None:
            params['season'] = season
        if episode is not None:
            params['video'] = episode
        await self.api('/watching/toggle', params)

    async def toggle_subscription(self, content_id):
        await self.api('/watching/togglewatchlist', {'id': content_id})

    async def toggle_bookmark(self, content_id, folder_id):
        await self.api(
            '/bookmarks/toggle-item',
            {
                'item': content_id,
                'folder': folder_id
            },
            method='POST'
        )

    async def get_current_device_info(self) -> Device:
        from models.Device import Device

        data = await self.api('/device/info')
        return Device(data.get('device', {}))

    async def update_device_setting(
        self,
        device_id: int,
        name: str,
        value: 'bool | int'
    ):
        await self.api(
            f'/device/{device_id}/settings',
            {name: value},
            'POST'
        )

    @staticmethod
    async def get_codes():
        params = {
            'grant_type': 'device_code',
            'client_id': kp.client_id,
            'client_secret': kp.client_secret
        }
        try:
            async with aiohttp.ClientSession(timeout=g.TIMEOUT) as s:
                response = await s.post(g.OAUTH_URL, params=params)
                result = await response.json()
                return result['user_code'], result['code']
        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as e:
            logger.warning('Failed to fetch registration codes: %s', e)
            return None

    @staticmethod
    async def check_registration(code):
        params = {
            'grant_type': 'device_token',
            'client_id': kp.client_id,
            'client_secret': kp.client_secret,
            'code': code
        }
        try:
            async with aiohttp.ClientSession(timeout=g.TIMEOUT) as s:
                response = await s.post(g.OAUTH_URL, params=params)
                result = await response.json()
                if result.get('error') is not None:
                    return None
                return result
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.warning('Failed to check device registration status: %s', e)
            return None

    async def refresh_tokens(self):
        params = {
            'grant_type': 'refresh_token',
            'client_id': kp.client_id,
            'client_secret': kp.client_secret,
            'refresh_token': self.refresh
        }
        try:
            async with aiohttp.ClientSession(timeout=g.TIMEOUT) as s:
                response = await s.post(g.OAUTH_URL, params=params)
                result = await response.json()
                if result.get('error') is not None:
                    return False

                db.update_tokens(
                    self.token,
                    result['access_token'],
                    result['refresh_token']
                )
                self.token = result['access_token']
                self.refresh = result['refresh_token']

                await self.close_session()

                return True
        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as e:
            logger.warning('Failed to refresh access token: %s', e)
            return False

    async def get_available_servers(self):
        return await self.fetch_list(
            '/references/server-location',
            Reference,
            default=[]
        )
