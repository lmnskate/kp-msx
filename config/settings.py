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
