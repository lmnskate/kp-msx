import logging
import os
import posixpath
import re
import tempfile
from urllib.parse import unquote, urlencode, urljoin, urlparse

import aiohttp

import config.globals as g
from config.settings import server
from util import db

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
}

CLIENT_TIMEOUT = aiohttp.ClientTimeout(
    connect=5,
    total=None,
    sock_read=30
)

KNOWN_DOMAINS: set[str] = set()

SESSION: aiohttp.ClientSession | None = None

NEW_DOMAINS_SINCE_DUMP = 0
DOMAINS_DUMP_INTERVAL = 10


class UnknownDomainError(Exception):
    pass


async def init_session() -> None:
    global SESSION
    SESSION = aiohttp.ClientSession(
        headers=HEADERS,
        timeout=CLIENT_TIMEOUT
    )


async def get_session() -> aiohttp.ClientSession:
    if SESSION is None or SESSION.closed:
        await init_session()

    return SESSION


async def close_session() -> None:
    global SESSION
    if SESSION is not None and not SESSION.closed:
        await SESSION.close()
    SESSION = None


async def extract_audio_tracks(
    url: str
) -> list[dict]:
    """Fetch the raw HLS master playlist and extract audio rendition metadata.

    Returns a list of dicts with keys: name, language, group, default.
    Used to give the TV player authoritative track names before it has to
    parse the manifest itself, which is useful when some video versions have
    generic/missing NAME attributes (e.g. "TRACK1") while others have full
    Russian names.
    """
    if not url:
        return []

    try:
        session = await get_session()
        async with session.get(url, headers={}) as response:
            if response.status != 200:
                logger.warning(
                    'Failed to fetch audio tracks from %s: status %s',
                    url,
                    response.status
                )
                return []

            text = await response.text()
    except Exception as exc:
        logger.warning(
            'Failed to fetch audio tracks from %s: %s',
            url,
            exc
        )
        return []

    tracks = []
    for line in text.splitlines():
        if not line.startswith('#EXT-X-MEDIA:'):
            continue
        if 'TYPE=AUDIO' not in line:
            continue

        name_match = re.search(r'NAME="([^"]*)"', line)
        lang_match = re.search(r'LANGUAGE="([^"]*)"', line)
        group_match = re.search(r'GROUP-ID="([^"]*)"', line)
        default_match = re.search(r'DEFAULT=(YES|NO)', line)

        name = name_match.group(1) if name_match else None
        if name:
            try:
                name = unquote(name)
            except Exception:
                pass

        tracks.append({
            'name': name,
            'language': lang_match.group(1) if lang_match else None,
            'group': group_match.group(1) if group_match else None,
            'default': default_match.group(1) == 'YES' if default_match else False,
        })

    return tracks


def merge_audio_track_names(
    tracks_by_video: list[list[dict]]
) -> list[list[dict]]:
    r"""Merge audio track names across video versions.

    Some KinoPub video versions (e.g. different FPS or cuts) expose generic
    or missing audio track names ("TRACK1") while another version of the same
    content has proper Russian names. This function builds a map of the best
    available name for each (language, occurrence) pair and applies it to all
    versions that only have a generic name.

    A name is considered generic if it matches TRACK\d*, AUDIO\d*, UND, or is
    just digits / empty.
    """
    generic_patterns = [
        re.compile(r'^TRACK\d*$', re.IGNORECASE),
        re.compile(r'^AUDIO\d*$', re.IGNORECASE),
        re.compile(r'^UND$', re.IGNORECASE),
        re.compile(r'^\d+$'),
    ]

    def is_generic(name):
        if not name:
            return True
        return any(p.match(name) for p in generic_patterns)

    # Find the best available name for each (language, occurrence)
    best_names = {}
    for tracks in tracks_by_video:
        language_counts = {}
        for track in tracks:
            language = track.get('language')
            occurrence = language_counts.get(language, 0)
            language_counts[language] = occurrence + 1
            key = (language, occurrence)
            if key not in best_names:
                best_names[key] = track.get('name')
            elif is_generic(best_names[key]) and not is_generic(track.get('name')):
                best_names[key] = track.get('name')

    # Apply best names back to each version
    result = []
    for tracks in tracks_by_video:
        language_counts = {}
        merged = []
        for track in tracks:
            language = track.get('language')
            occurrence = language_counts.get(language, 0)
            language_counts[language] = occurrence + 1
            key = (language, occurrence)
            new_track = track.copy()
            if is_generic(track.get('name')) and key in best_names:
                candidate = best_names[key]
                if not is_generic(candidate):
                    new_track['name'] = candidate
            merged.append(new_track)
        result.append(merged)

    return result


def make_proxy_url(
    url
):
    domain = urlparse(url).netloc
    remember_domain(domain)

    return f'{server.base_url}/msx/proxy?' + urlencode({'url': url})


def make_subtitle_url(
    url
):
    domain = urlparse(url).netloc
    remember_domain(domain)

    return f'{server.base_url}/msx/subtitle?' + urlencode({'url': url})


def domain_exists(
    domain
):
    if domain in KNOWN_DOMAINS:
        return True

    if db.get_domain(domain) is not None:
        KNOWN_DOMAINS.add(domain)
        return True

    return False


def remember_domain(
    domain
):
    global NEW_DOMAINS_SINCE_DUMP

    if not domain or domain_exists(domain):
        return

    db.add_domain(domain)
    KNOWN_DOMAINS.add(domain)
    NEW_DOMAINS_SINCE_DUMP += 1
    maybe_dump_domains_file()


def remember_url(
    url
):
    if url:
        remember_domain(urlparse(url).netloc)


def registrable_domain(
    domain
):
    """Reduce a hostname to its registrable domain (second-level + TLD),
    e.g. 'cdn1.example.com' -> 'example.com'. Common compound suffixes
    ('co.uk' etc.) are taken into account; IPs and already-short hostnames
    pass through unchanged."""
    host = domain.split('@')[-1].split(':')[0]
    labels = host.split('.')
    if len(labels) <= 2 or labels[-1].isdigit():
        return host

    suffix = '.'.join(labels[-2:])
    if suffix in g.COMPOUND_TLDS:
        return '.'.join(labels[-3:])

    return suffix


def dump_domains_file():
    try:
        domains = {
            registrable_domain(domain) for domain in db.get_domains()
        }
        path = g.CDN_DOMAINS_FILE
        directory = os.path.dirname(path) or '.'
        os.makedirs(directory, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(
            dir=directory,
            prefix='.cdn-domains-'
        )
        try:
            with os.fdopen(fd, 'w') as f:
                for domain in sorted(domains):
                    f.write(domain + '\n')
            os.replace(tmp_path, path)
        except Exception:
            os.unlink(tmp_path)
            raise
    except OSError:
        logger.warning(
            'Failed to write %s',
            g.CDN_DOMAINS_FILE
        )


def maybe_dump_domains_file(
    force=False
):
    global NEW_DOMAINS_SINCE_DUMP

    if force or NEW_DOMAINS_SINCE_DUMP >= DOMAINS_DUMP_INTERVAL:
        NEW_DOMAINS_SINCE_DUMP = 0
        dump_domains_file()


# Bootstrap the domains file from the DB collected by previous runs
maybe_dump_domains_file(force=True)


def check_url(
    url
):
    domain = urlparse(url).netloc
    if not domain_exists(domain):
        raise UnknownDomainError('Unknown domain')

    return True


def rewrite_domain(
    url: str,
    content: str
) -> str:
    domain_info = urlparse(url)
    base_url = f'{domain_info.scheme}://{domain_info.netloc}'
    if domain_info.path:
        base_url = urljoin(
            base_url + '/',
            posixpath.dirname(domain_info.path) + '/'
        )

    def _rewrite_url(
        ref: str
    ):
        if ref.startswith(server.base_url):
            return ref

        if ref.startswith(('http://', 'https://')):
            return make_proxy_url(ref)

        resolved = urljoin(base_url, ref)

        return make_proxy_url(resolved)

    def _rewrite_line(
        line: str
    ):
        if not line:
            return line

        if line.startswith('#'):
            return re.sub(
                r'URI="([^"]*)"',
                lambda m: f'URI="{_rewrite_url(m.group(1))}"',
                line
            )

        stripped = line.strip()
        if not stripped:
            return line

        return _rewrite_url(stripped)

    return '\n'.join(_rewrite_line(line) for line in content.splitlines()) + '\n'


def filter_audio_track(
    content: str,
    audio_name: str
) -> str:
    """Keep only the requested audio rendition (matched by NAME) in a master
    playlist. Used for server-side audio switching on players whose platform
    does not expose the audioTracks API."""
    lines = []
    for line in content.splitlines():
        if line.startswith('#EXT-X-MEDIA:') and 'TYPE=AUDIO' in line:
            match = re.search(
                r'NAME="([^"]*)"',
                line
            )
            name = match.group(1) if match else None
            if name != audio_name and unquote(name or '') != audio_name:
                continue
            if 'DEFAULT=' in line:
                line = re.sub(
                    r'DEFAULT=(YES|NO)',
                    'DEFAULT=YES',
                    line
                )
            else:
                line += ',DEFAULT=YES'
            if 'AUTOSELECT=' in line:
                line = re.sub(
                    r'AUTOSELECT=(YES|NO)',
                    'AUTOSELECT=YES',
                    line
                )
        lines.append(line)

    return '\n'.join(lines) + '\n'


async def get(
    url,
    audio_name=None,
    client_headers=None
):
    request_headers = {}
    if client_headers and 'Range' in client_headers:
        request_headers['Range'] = client_headers['Range']

    session = await get_session()
    response = await session.get(url, headers=request_headers)

    content_type = response.headers.get('content-type')
    response_headers = {}
    for header in ('Content-Range', 'Accept-Ranges'):
        if header in response.headers:
            response_headers[header] = response.headers[header]

    is_text_playlist = ((
        content_type is not None and 'mpegurl' in content_type.lower()
    ) or urlparse(url).path.lower().split('?')[0].endswith('.m3u8'))

    if is_text_playlist:
        content = await response.read()
        await response.release()
        text_content = content.decode('utf-8')
        text_content = rewrite_domain(
            url,
            text_content
        )
        if audio_name:
            text_content = filter_audio_track(
                text_content,
                audio_name
            )

        return response.status, content_type, response_headers, text_content.encode('utf-8')

    async def _chunks():
        try:
            async for chunk in response.content.iter_any():
                yield chunk
        finally:
            await response.release()

    return response.status, content_type, response_headers, _chunks()


def srt_to_vtt(
    content: bytes
) -> bytes:
    text = content.decode(
        'utf-8-sig',
        errors='replace'
    )
    if text.lstrip().startswith('WEBVTT'):
        return content

    text = re.sub(
        r'(\d{1,2}:\d{2}:\d{2}),(\d{3})',
        r'\1.\2',
        text
    )

    return ('WEBVTT\n\n' + text.lstrip()).encode('utf-8')


async def get_subtitle(
    url
):
    session = await get_session()
    async with session.get(url) as response:
        content = await response.read()

        if response.status != 200:
            return response.status, response.headers.get('content-type'), content

        return response.status, 'text/vtt', srt_to_vtt(content)
