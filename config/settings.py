from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='SERVER_',
        extra='ignore'
    )

    host: str
    port: int = 1234
    scheme: str = 'http'
    sqlite_url: str = './kp-sqlite.db'

    @property
    def base_url(self) -> str:
        if '://' in self.host:
            parsed = urlparse(self.host)
            return f'{parsed.scheme}://{parsed.netloc}'
        return f'{self.scheme}://{self.host}:{self.port}'


class KPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='KP_',
        extra='ignore'
    )

    client_id: str
    client_secret: str
    protocol: str = 'hls4'
    quality: str = '1080p'


server = ServerSettings()
kp = KPSettings()
