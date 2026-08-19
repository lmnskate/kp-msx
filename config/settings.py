from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE_PATH = Path(__file__).parent.parent / '.env'


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE_PATH,
        env_prefix='SERVER_',
        extra='ignore'
    )

    host: str
    port: int = 1234
    scheme: Literal['http', 'https'] = 'http'
    sqlite_url: str = './kp-sqlite.db'
    # Where uvicorn actually listens. Defaults to 0.0.0.0:port; override both
    # when a reverse proxy (e.g. nginx) holds the public port on the same
    # machine — see "Running behind nginx" in README.md.
    bind_host: str = '0.0.0.0'
    bind_port: int | None = None
    workers: int = 1
    proxy_headers: bool = False

    @property
    def base_url(
        self
    ) -> str:
        if self.port in (80, 443):
            return f'{self.scheme}://{self.host}'

        return f'{self.scheme}://{self.host}:{self.port}'


class KPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE_PATH,
        env_prefix='KP_',
        extra='ignore'
    )

    client_id: str
    client_secret: str
    protocol: Literal['hls', 'hls2', 'hls4', 'http'] = 'hls4'
    quality: Literal['2160p', '1080p', '720p', '480p'] = '1080p'


server = ServerSettings()
kp = KPSettings()
