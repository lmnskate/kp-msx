from urllib.parse import urlparse, urlencode
import aiohttp
import config
from util import db
import re


def make_proxy_url(url):
    domain = urlparse(url).netloc
    remember_domain(domain)
    return f'{config.MSX_HOST}/msx/proxy?' + urlencode({'url': url})

def domain_exists(domain):
    if db.get_domain(domain) is None:
        return False
    return True

def remember_domain(domain):
    if not domain_exists(domain):
        db.add_domain(domain)

def check_url(url):
    domain = urlparse(url).netloc
    if not domain_exists(domain):
        raise Exception('Unknown domain')
    return True

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
}

def rewrite_domain(url: str, content: str) -> str:
    domain_info = urlparse(url)
    prefix = domain_info.scheme + '://' + domain_info.netloc

    def _d(x: re.Match):
        u = f'{config.MSX_HOST}/msx/proxy?' + urlencode({'url': prefix + '/' + x.group(1)})
        return f'URI="{u}"'

    content = re.sub('URI="/(.*)"', lambda x: _d(x), content)
    return content


async def get(url):
    async with aiohttp.ClientSession(headers=HEADERS, timeout=aiohttp.ClientTimeout(total=5)) as s:
        response = await s.get(url)
        content = await response.read()
        if isinstance(content, bytes):
            text_content = content.decode('utf-8')
            text_content = rewrite_domain(url, text_content)
            content = text_content.encode('utf-8')
        return response.status, response.headers.get('content-type'), content
