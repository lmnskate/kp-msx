import re
from urllib.parse import unquote, urlencode, urlparse

import aiohttp

from config.settings import server
from util import db

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
}

KNOWN_DOMAINS: set[str] = set()

SESSION: aiohttp.ClientSession | None = None


async def get_session() -> aiohttp.ClientSession:
    global SESSION
    if SESSION is None or SESSION.closed:
        SESSION = aiohttp.ClientSession(
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=5)
        )
    return SESSION


async def close_session() -> None:
    global SESSION
    if SESSION is not None and not SESSION.closed:
        await SESSION.close()
    SESSION = None


def make_proxy_url(url):
    domain = urlparse(url).netloc
    remember_domain(domain)
    return f'{server.base_url}/msx/proxy?' + urlencode({'url': url})


def make_subtitle_url(url):
    domain = urlparse(url).netloc
    remember_domain(domain)
    return f'{server.base_url}/msx/subtitle?' + urlencode({'url': url})


def domain_exists(domain):
    if domain in KNOWN_DOMAINS:
        return True

    if db.get_domain(domain) is not None:
        KNOWN_DOMAINS.add(domain)
        return True

    return False


def remember_domain(domain):
    if not domain_exists(domain):
        db.add_domain(domain)
    KNOWN_DOMAINS.add(domain)


def check_url(url):
    domain = urlparse(url).netloc
    if not domain_exists(domain):
        raise Exception('Unknown domain')
    return True


def rewrite_domain(url: str, content: str) -> str:
    domain_info = urlparse(url)
    prefix = f'{domain_info.scheme}://{domain_info.netloc}'

    def replace_match(x: re.Match):
        a, b, c = x.groups()
        r = f'{server.base_url}/msx/proxy?' + urlencode({'url': f'{prefix}/{b}'})
        return a + r + c

    content = re.sub(
        '(^|URI=")/(.*?)($|")',
        replace_match,
        content,
        flags=re.MULTILINE
    )

    return content


def filter_audio_track(content: str, audio_name: str) -> str:
    """Keep only the requested audio rendition (matched by NAME) in a master
    playlist. Used for server-side audio switching on players whose platform
    does not expose the audioTracks API."""
    lines = []
    for line in content.splitlines():
        if line.startswith('#EXT-X-MEDIA:') and 'TYPE=AUDIO' in line:
            match = re.search(r'NAME="([^"]*)"', line)
            name = match.group(1) if match else None
            if name != audio_name and unquote(name or '') != audio_name:
                continue
            if 'DEFAULT=' in line:
                line = re.sub(r'DEFAULT=(YES|NO)', 'DEFAULT=YES', line)
            else:
                line += ',DEFAULT=YES'
            if 'AUTOSELECT=' in line:
                line = re.sub(r'AUTOSELECT=(YES|NO)', 'AUTOSELECT=YES', line)
        lines.append(line)
    return '\n'.join(lines) + '\n'


async def get(url, audio_name=None):
    session = await get_session()
    async with session.get(url) as response:
        content = await response.read()
        content_type = response.headers.get('content-type')

        is_text_playlist = ((
            content_type is not None and 'mpegurl' in content_type.lower()
        ) or url.lower().endswith('.m3u8'))

        if is_text_playlist:
            text_content = content.decode('utf-8')
            text_content = rewrite_domain(url, text_content)
            if audio_name:
                text_content = filter_audio_track(text_content, audio_name)
            content = text_content.encode('utf-8')

        return response.status, content_type, content


def srt_to_vtt(content: bytes) -> bytes:
    text = content.decode('utf-8-sig', errors='replace')
    if text.lstrip().startswith('WEBVTT'):
        return content

    text = re.sub(
        r'(\d{1,2}:\d{2}:\d{2}),(\d{3})',
        r'\1.\2',
        text
    )
    return ('WEBVTT\n\n' + text.lstrip()).encode('utf-8')


async def get_subtitle(url):
    session = await get_session()
    async with session.get(url) as response:
        content = await response.read()
        return response.status, 'text/vtt', srt_to_vtt(content)
