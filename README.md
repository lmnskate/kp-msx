# Kinopub for Media Station X

Watch [KinoPub](https://kino.pub) on your TV through [Media Station X](https://msx.benzac.de/).

This is a small server that sits between your TV and the KinoPub API — useful when direct access to KinoPub is blocked in your region. Deploy it somewhere with unrestricted access, point MSX at it, and you're set.

Fork of [slonopot/kp-msx](https://github.com/slonopot/kp-msx) with SQLite instead of MongoDB and other improvements.

## Setup

Python 3.12+ required. No external database needed — SQLite is created automatically.

```bash
# Clone and install
git clone https://github.com/llmnskate/kp-msx.git
cd kp-msx
python -m venv .venv
.venv/bin/pip install -r requirements.txt

# Configure
cp .env.example .env

# Running
.venv/bin/python main.py
```

`python main.py` is the canonical way to run the server, development or
production: it binds `0.0.0.0:SERVER_PORT` and runs uvicorn with
`SERVER_WORKERS` processes and `SERVER_PROXY_HEADERS`. Everything is
configured through `.env` — no command-line flags needed.

To verify, open `http://<your-ip>:1234/msx/start.json` in a browser.

Then on your TV: open MSX → Settings → Start Parameter → enter `http://<your-ip>:1234`.

## Running as a systemd service (Linux)

Create a service file:

```bash
sudo nano /etc/systemd/system/kp-msx.service
```

Paste the following (adjust paths if your installation differs):

```ini
[Unit]
Description=KP-MSX Service
After=network.target
Wants=network.target

[Service]
User=user
Group=user

WorkingDirectory=/home/user/kp-msx

# main.py reads .env itself; workers and proxy-headers are configured there.
ExecStart=/home/user/kp-msx/.venv/bin/python main.py

Restart=always
RestartSec=5

KillSignal=SIGINT
TimeoutStopSec=30

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable kp-msx
sudo systemctl start kp-msx

# Check status
sudo systemctl status kp-msx

# View logs
journalctl -u kp-msx -f
```

## Environment variables

Variables are loaded from `.env`. See `.env.example` for a template.

### Server (`SERVER_` prefix)

| Variable             | Description                                        | Default           |
|----------------------|----------------------------------------------------|-------------------|
| `SERVER_HOST`        | Hostname or IP of your server (used to generate links) | **required**      |
| `SERVER_PORT`        | Public port used to generate links                  | `1234`            |
| `SERVER_SCHEME`      | Scheme for public links (`http` or `https`)         | `http`            |
| `SERVER_SQLITE_URL`  | SQLite database path                                | `./kp-sqlite.db`  |
| `SERVER_WORKERS`     | Number of uvicorn worker processes                  | `1`               |
| `SERVER_PROXY_HEADERS` | Trust `X-Forwarded-*` headers from a reverse proxy (`true`/`false`) | `false` |

### KinoPub API (`KP_` prefix)

| Variable           | Description                                           | Default  |
|--------------------|-------------------------------------------------------|----------|
| `KP_CLIENT_ID`     | KinoPub API client ID (write to support@kino.pub)     | **required** |
| `KP_CLIENT_SECRET`  | KinoPub API client secret (write to support@kino.pub) | **required** |
| `KP_PROTOCOL`      | Streaming protocol (`hls`, `hls2`, `hls4`, `http`)    | `hls4`   |
| `KP_QUALITY`       | Preferred video quality (`2160p`, `1080p`, `720p`, `480p`); falls back to best available | `1080p` |

## Project structure

```
main.py              # FastAPI app, middleware, router includes
config/
    settings.py     # Pydantic settings (ServerSettings, KPSettings), loaded from .env
    globals.py      # Constants: API URLs, timeouts, UI IDs, player URLs
icons/              # Custom SVG icons
routers/
    static.py       # Static files and start.json
    registration.py # Device registration
    content.py      # Browsing, playback, bookmarks
    settings.py     # Per-device settings
    proxy.py        # Media proxy, HLS rewriting, error pages
models/             # Data models (Content, Device, KinoPub client, etc.)
util/
    msx/            # MSX JSON response builders (core, menu, settings, registration, player)
    proxy.py        # Domain-allowlist proxy
    db.py           # SQLite storage
    sqlite_migrations.py # Schema migrations
pages/              # Static HTML/JS: self-hosted hlsx/html5x video player plugins, helper pages
```