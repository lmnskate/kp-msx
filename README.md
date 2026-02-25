# Kinopub for Media Station X

Watch [KinoPub](https://kino.pub) on your TV through [Media Station X](https://msx.benzac.de/).

This is a small server that sits between your TV and the KinoPub API — useful when direct access to KinoPub is blocked in your region. Deploy it somewhere with unrestricted access, point MSX at it, and you're set.

Fork of [slonopot/kp-msx](https://github.com/slonopot/kp-msx) with SQLite instead of MongoDB and other improvements.

## Setup

Python 3.12+ required. No external database needed — SQLite is created automatically.

```bash
# Clone and install
git clone https://github.com/anon/kp-msx.git
cd kp-msx
python -m venv .venv
.venv/bin/pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env — at minimum, set KP_MSX_MSX_HOST to http://<your-ip>:1234
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

ExecStart=/home/user/kp-msx/venv/bin/uvicorn api:app --host 0.0.0.0 --port 1234

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

All variables use the `KP_MSX_` prefix and are loaded from `.env`. See `.env.example` for a template.

| Variable                          | Description                                           | Default           |
|-----------------------------------|-------------------------------------------------------|------------------|
| `KP_MSX_MSX_HOST`                 | Public URL of your server (used to generate links)    | **required**     |
| `KP_MSX_PORT`                     | Port when running via `python api.py`                 | `10000`          |
| `KP_MSX_SQLITE_URL`               | SQLite database path                                  | `./kp-sqlite.db` |
| `KP_MSX_PROTOCOL`                 | Streaming protocol (`hls`, `hls2`, `hls4`, `http`)    | `hls4`           |
| `KP_MSX_QUALITY`                  | Video quality for `http`/`hls` protocols              | max available    |
| `KP_MSX_PLAYER`                   | Video player plugin URL                               | built-in hlsx    |
| `KP_MSX_ALTERNATIVE_PLAYER`       | Fallback player for older devices                     | html5x           |
| `KP_MSX_TIZEN`                    | Use Samsung Tizen built-in player instead of plugin   | `false`          |
| `KP_MSX_KP_CLIENT_ID`             | KinoPub API client ID (write to support@kino.pub)     | **required**     |
| `KP_MSX_KP_CLIENT_SECRET`         | KinoPub API client secret (write to support@kino.pub) | **required**     |
| `KP_MSX_POSTERS_HOST_REPLACEMENT` | Override poster CDN hostname                          | —                |

On Render.com, `RENDER_EXTERNAL_URL` is used automatically in place of `KP_MSX_MSX_HOST`.

## Project structure

```
api.py              # FastAPI app, middleware, router includes
config.py           # Settings (pydantic-settings, loaded from .env)
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
pages/              # Static HTML/JS (subtitle timing tool at /subtitleShifter)
```