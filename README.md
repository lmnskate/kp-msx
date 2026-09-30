<div align="center">

# KP-MSX

**Watch [KinoPub](https://kino.pub) on your TV through [Media Station X](https://msx.benzac.de/)**

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-embedded-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

[Features](#features) •
[Quick Start](#quick-start) •
[Management](#management) •
[Configuration](#configuration) •
[Security](#security)

</div>

---

## Features

- KinoPub on TV: menu, categories, search, bookmarks, history, collections, TV channels
- Cross-device resume — playback progress is synced back to KinoPub
- Built-in media proxy — the TV only talks to this server (works where KinoPub is blocked)
- Two self-hosted player plugins (hls.js default, HTML5 alternative) with server-side audio switching
- Customizable menu — Search, Bookmarks, History, and Settings always stay
- SQLite storage, zero external services

Fork of [slonopot/kp-msx](https://github.com/slonopot/kp-msx) — SQLite instead
of MongoDB, Docker deployment, and more.

## Quick Start

Requires Docker with the Compose plugin.

```bash
git clone https://github.com/llmnskate/kp-msx.git
cd kp-msx
cp .env.example .env   # edit SERVER_HOST, KP_CLIENT_ID, KP_CLIENT_SECRET
./kp-msx.sh start
```

Check: `curl http://<your-ip>:1234/msx/start.json`
TV: **MSX → Settings → Start Parameter** → `http://<your-ip>:1234`.

Upgrading from a non-Docker install: put your existing database at
`data/kp-sqlite.db` before the first start — it will be picked up as-is
(migrations run automatically on startup).

The stack: `server` (FastAPI app, internal `:8000`) + `nginx` (public
`:1234`, serves `/icons/` from disk). State lives in `./data` (SQLite) and
survives rebuilds and updates.

## Management

```bash
./kp-msx.sh start     # build and start the stack
./kp-msx.sh status    # stack status and the TV entry point
./kp-msx.sh logs      # follow logs (optionally: ./kp-msx.sh logs server)
./kp-msx.sh restart   # recreate containers, re-reading .env and conf/
./kp-msx.sh stop      # stop everything (data is kept)
./kp-msx.sh update    # rebuild from source and restart (e.g. after git pull)
./kp-msx.sh backup    # consistent DB backup into ./backups/ (safe on a live DB)
./kp-msx.sh shell     # shell inside the server container
```

Restore a backup:

```bash
./kp-msx.sh stop
cp backups/kp-sqlite-YYYYMMDD-HHMMSS.db data/kp-sqlite.db
./kp-msx.sh start
```

`conf/nginx.conf` and `src/icons/` are bind-mounted — changes apply with
`./kp-msx.sh restart`, no rebuild.

## Development

Requires Python 3.12+.

```bash
python -m venv .venv
.venv/bin/pip install -r src/requirements.txt
.venv/bin/python src/main.py
```

## Configuration

Required in `.env`:

- `SERVER_HOST` — IP or domain of your server, reachable from the TV
- `KP_CLIENT_ID`, `KP_CLIENT_SECRET` — write to support@kino.pub

`SERVER_PORT` (default `1234`) is the only other commonly changed one.
Everything else has sane defaults — full list with allowed values:
`src/config/settings.py`.

## Security

- The `id` query parameter is the device credential: anyone who knows it
  controls the linked KinoPub account. Keep URLs with `id=...` private.
- `/msx/proxy` and `/msx/subtitle` are unauthenticated relays restricted to
  remembered KinoPub CDN domains. Restrict access at the firewall level if
  that matters to you.

## Project Structure

```
src/                # App service: code + Dockerfile + requirements.txt (compose build context)
    main.py         # FastAPI app, middleware
    config/         # Settings (.env), constants
    routers/        # HTTP endpoints
    models/         # KinoPub API wrappers, Device, MSX rendering
    util/           # MSX JSON builders, proxy, SQLite
    pages/          # Self-hosted player plugins, helper pages
    icons/          # SVG icons
conf/               # nginx config
data/               # SQLite DB (bind-mounted, gitignored)
backups/            # DB backups (gitignored)
kp-msx.sh           # Management script
docker-compose.yml  # server + nginx
```

## Acknowledgments

[slonopot/kp-msx](https://github.com/slonopot/kp-msx) ·
[Media Station X](https://msx.benzac.de/) ·
[msx-hlsx](https://github.com/slonopot/msx-hlsx)
