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

## Running behind nginx (optional)

nginx is not required — the app works fine on its own. Use it if you want a
proper reverse proxy in front: nginx holds the public port, serves the icons
from disk, and the app stays hidden on localhost.

The split of responsibilities:

- **nginx** — binds the public address (`1234` in this example), proxies
  everything to the app, serves `/icons/` directly.
- **The app** — binds a private localhost address (`127.0.0.1:8000`) via
  `SERVER_BIND_HOST`/`SERVER_BIND_PORT`, while `SERVER_HOST`/`SERVER_PORT`
  keep the **public** values so the links generated for the TV point at nginx.

### 1. Configure the app (`.env`)

```ini
SERVER_HOST=<your-server-ip>   # public address used in generated links
SERVER_PORT=1234               # public nginx port
SERVER_BIND_HOST=127.0.0.1
SERVER_BIND_PORT=8000
SERVER_PROXY_HEADERS=true
```

Start the app as usual (`.venv/bin/python main.py` or the systemd unit above)
and verify it listens on the bind address:

```bash
curl http://127.0.0.1:8000/msx/start.json
```

### 2. Configure nginx

Create `/etc/nginx/sites-available/kp-msx` (adjust the IP and paths):

```nginx
upstream kp_msx {
    server 127.0.0.1:8000;   # must match SERVER_BIND_HOST:SERVER_BIND_PORT
}

server {
    listen 1234;             # must match SERVER_PORT
    server_name <your-server-ip>;

    # Serve icons directly from disk, bypassing the app
    location /icons/ {
        alias /home/user/kp-msx/icons/;
        access_log off;
        expires 7d;
        add_header Access-Control-Allow-Origin * always;
    }

    location / {
        proxy_pass http://kp_msx;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_buffering off;        # don't buffer video streams
        proxy_read_timeout 300s;    # long-lived HLS requests
    }
}
```

Enable and start it:

```bash
sudo ln -s /etc/nginx/sites-available/kp-msx /etc/nginx/sites-enabled/kp-msx
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Verify end to end

```bash
curl http://<your-server-ip>:1234/msx/start.json   # through nginx
```

Then point the TV at `http://<your-server-ip>:1234` as usual.

Troubleshooting: a `502 Bad Gateway` with `connect() failed ... 127.0.0.1:8000`
in the nginx error log means the app is not listening on the bind address —
check `SERVER_BIND_HOST`/`SERVER_BIND_PORT` against the `upstream` block.

For HTTPS, terminate TLS in nginx (e.g. with certbot) and set
`SERVER_SCHEME=https` and `SERVER_PORT=443` in `.env`.

## Environment variables

Variables are loaded from `.env`. See `.env.example` for a template.

### Server (`SERVER_` prefix)

| Variable             | Description                                        | Default           |
|----------------------|----------------------------------------------------|-------------------|
| `SERVER_HOST`        | Hostname or IP of your server (used to generate links) | **required**      |
| `SERVER_PORT`        | Public port used to generate links                  | `1234`            |
| `SERVER_SCHEME`      | Scheme for public links (`http` or `https`)         | `http`            |
| `SERVER_SQLITE_URL`  | SQLite database path                                | `./kp-sqlite.db`  |
| `SERVER_BIND_HOST`   | Address the server actually listens on (see "Running behind nginx") | `0.0.0.0` |
| `SERVER_BIND_PORT`   | Port the server actually listens on (override together with `SERVER_BIND_HOST`) | `SERVER_PORT` |
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