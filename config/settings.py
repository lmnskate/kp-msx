from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='SERVER_',
        extra='ignore'
    )

    host: str
    port: int = 1234
    sqlite_url: str = './kp-sqlite.db'


class KPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='KP_',
        extra='ignore'
    )

    client_id: str
    client_secret: str
    protocol: str = 'hls4'


server = ServerSettings()
kp = KPSettings()
