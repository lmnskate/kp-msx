from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='KP_MSX_',
        extra='ignore',
    )

    msx_host: str | None = None
    sqlite_url: str = './kp-sqlite.db'
    port: int = 10000
    player: str = 'https://slonopot.github.io/msx-hlsx/hlsx.html'
    alternative_player: str = 'http://msx.benzac.de/plugins/html5x.html'
    kp_client_id: str = 'xbmc'
    kp_client_secret: str = 'cgg3gtifu46urtfp2zp1nqtba0k2ezxh'
    quality: str | None = None
    protocol: str = 'hls4'
    tizen: bool = False
    posters_host_replacement: str | None = None
    render_external_url: str | None = Field(
        default=None,
        validation_alias='RENDER_EXTERNAL_URL',
    )

    @field_validator('tizen', mode='before')
    @classmethod
    def parse_tizen(cls, value):
        if isinstance(value, str):
            return value.strip().lower() in {'1', 'true', 'yes', 'on'}
        return value


settings = Settings()

MSX_HOST = settings.render_external_url or settings.msx_host
SQLITE_URL = settings.sqlite_url
PORT = settings.port
PLAYER = settings.player
ALTERNATIVE_PLAYER = settings.alternative_player
KP_CLIENT_ID = settings.kp_client_id
KP_CLIENT_SECRET = settings.kp_client_secret
QUALITY = settings.quality
PROTOCOL = settings.protocol
TIZEN = settings.tizen
POSTERS_HOST_REPLACEMENT = settings.posters_host_replacement
