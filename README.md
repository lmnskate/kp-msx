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
# Edit .env — at minimum, set SERVER_HOST to http://<your-ip>:1234
```

> On Windows, use `.venv\Scripts\pip` and `.venv\Scripts\uvicorn` instead of `.venv/bin/`.

## Running

```bash
.venv/bin/uvicorn --host 0.0.0.0 --port 1234 api:app
```

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

EnvironmentFile=/home/user/kp-msx/.env

ExecStart=/home/user/kp-msx/.venv/bin/uvicorn api:app --host 0.0.0.0 --port 1234 --proxy-headers --workers 4

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
| `SERVER_HOST`        | Public URL of your server (used to generate links) | **required**      |
| `SERVER_PORT`        | Port when running via `python api.py`              | `1234`            |
| `SERVER_SQLITE_URL`  | SQLite database path                               | `./kp-sqlite.db`  |

### KinoPub API (`KP_` prefix)

| Variable           | Description                                           | Default  |
|--------------------|-------------------------------------------------------|----------|
| `KP_CLIENT_ID`     | KinoPub API client ID (write to support@kino.pub)     | **required** |
| `KP_CLIENT_SECRET`  | KinoPub API client secret (write to support@kino.pub) | **required** |
| `KP_PROTOCOL`      | Streaming protocol (`hls`, `hls2`, `hls4`, `http`)    | `hls4`   |

## Project structure

```
api.py              # FastAPI app, middleware, router includes
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
    msx.py          # MSX JSON response builders
    proxy.py        # Domain-allowlist proxy
    db.py           # SQLite storage
    sqlite_migrations.py # Schema migrations
pages/              # Static HTML/JS (subtitle timing tool at /subtitleShifter)
```