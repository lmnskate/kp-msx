<div align="center">

# KP-MSX

**Watch [KinoPub](https://kino.pub) on your TV through [Media Station X](https://msx.benzac.de/)**

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-embedded-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

[Features](#features) •
[Quick Start](#quick-start) •
[Connecting a TV](#connecting-a-tv) •
[Management](#management) •
[Configuration](#configuration) •
[Domain and TLS](#domain-and-tls) •
[Security](#security) •
[Project Structure](#project-structure)

</div>

---

## Features

- KinoPub on TV: menu, categories, search, bookmarks, history, collections, TV channels
- Cross-device resume — playback progress is synced back to KinoPub
- Built-in media proxy — the TV only talks to this server (works where KinoPub is blocked)
- Two self-hosted player plugins (hls.js default, HTML5 alternative) with server-side audio switching
- Customizable menu — Search, Bookmarks, History, and Settings always stay
- Device management from the management script — list, reset, or delete
  registered devices (`admin user ...`) without touching the database
- SQLite storage, zero external services

Fork of [slonopot/kp-msx](https://github.com/slonopot/kp-msx) — SQLite instead
of MongoDB, Docker deployment, HTTPS only, and more.

## Quick Start

Development (no Docker):

```bash
python -m venv .venv
.venv/bin/pip install -r src/requirements.txt
cp .env.example .env   # edit SERVER_HOST, KP_CLIENT_ID, KP_CLIENT_SECRET
.venv/bin/python src/main.py
```

Smoke check: `curl http://localhost:1234/msx/start.json`. Requires Python 3.13+.

Production deployment is Docker Compose (see [Management](#management)) and
speaks **HTTPS only** — see [Domain and TLS](#domain-and-tls).

## Connecting a TV

Point the MSX start parameter at the server — **MSX → Settings → Start
Parameter** → `https://<your-domain>/msx/start.json`.

The first launch walks through KinoPub activation (enter the shown code at
kino.pub/device); afterwards the TV opens straight into the menu.

## Management

```bash
./kp-msx.sh install   # build/pull the images, prepare the data dirs (creates .env to edit)
./kp-msx.sh start     # start the stack (requires: install + a certificate)
./kp-msx.sh restart   # recreate containers, re-reading .env and conf/
./kp-msx.sh status    # container status (state, health, uptime, ports) + the TV URL
./kp-msx.sh stop      # stop everything (data is kept)
./kp-msx.sh backup    # consistent DB backup into ./backups/ (safe on a live DB)
./kp-msx.sh admin     # device management tree; run it bare to see its commands
                      # (admin user list|delete <id>|reset <id>, each with --help)
```

The stack: `server` (FastAPI app, internal `:8000`) + `nginx` (public `:443`
with TLS; `:80` only redirects to https; `/icons/` is served from disk).
State lives in `./data` (SQLite) and survives rebuilds and updates.
`conf/nginx.conf` and `src/icons/` are bind-mounted — config changes apply
with `./kp-msx.sh restart`, no rebuild. Backend (image) changes need a
rebuild: run `./kp-msx.sh install` again (it is idempotent).

After `git pull` (code changes): `./kp-msx.sh install && ./kp-msx.sh restart`.

Restore a backup:

```bash
./kp-msx.sh stop
cp backups/kp-sqlite-YYYYMMDD-HHMMSS.db data/kp-sqlite.db
./kp-msx.sh start
```

Upgrading from a non-Docker install: put your existing database at
`data/kp-sqlite.db` before the first start — it will be picked up as-is
(migrations run automatically on startup).

## Configuration

Everything is read from environment variables / `.env`
(`src/config/settings.py` for the authoritative list).

Required:

- `SERVER_HOST` — domain name of your server, reachable from the TV; all
  absolute URLs handed to the TV are built from it, and the TLS certificate
  must be issued for this exact name. The deployment is HTTPS-only, so an IP
  will not do here — see below for a free domain.
- `KP_CLIENT_ID`, `KP_CLIENT_SECRET` — KinoPub OAuth app credentials,
  request from support@kino.pub

Preset for the Docker deployment (change only if you deviate from the
defaults):

- `SERVER_PORT` — `443`
- `SERVER_SCHEME` — `https`

Commonly changed:

- `KP_PROTOCOL` — preferred streaming protocol: `hls4` (default), `hls2`,
  `hls` or `http`; lower-priority protocols are used as fallback
- `KP_QUALITY` — target quality: `1080p` (default), `2160p`, `720p`, `480p`

Rarely needed (Docker overrides them): `SERVER_BIND_HOST`, `SERVER_BIND_PORT`,
`SERVER_SQLITE_URL` (defaults to `./data/kp-sqlite.db`), `SERVER_WORKERS`,
`SERVER_PROXY_HEADERS`.

## Domain and TLS

The Docker deployment speaks HTTPS only: nginx serves the app on `:443` and
refuses to start without a certificate — `./kp-msx.sh start` checks for it and
prints the exact command to issue one. Port 80 only redirects to https.

**Getting a domain.** Any domain works; a free one is enough. Services like
[DuckDNS](https://www.duckdns.org) (or no-ip.com and similar) give you a
subdomain — say `<your-domain-fqdn>` — for free: sign in (a GitHub/Google
account is enough), create the name, and point it at your server's public IP.
DuckDNS names just need an occasional re-confirmation click to stay yours.

**Setup, from scratch:**

1. Point the domain at your server's IP; open ports 80 and 443 on the
   firewall (`sudo ufw allow 80/tcp && sudo ufw allow 443/tcp`, plus the
   cloud provider's security group if any).
2. `./kp-msx.sh install` — builds the images, creates `.env` and the data
   directories. Then edit `.env`: `SERVER_HOST=<your-domain-fqdn>`
   (`SERVER_PORT`/`SERVER_SCHEME` are already 443/https).
3. Install certbot if needed (`sudo apt install certbot`) and issue the
   certificate — under the fixed name `kp-msx`. `--standalone` spins up its
   own temporary web server on port 80, so this works while the stack is
   still stopped:

   ```bash
   sudo certbot certonly --standalone -d <your-domain-fqdn> --cert-name kp-msx \
       --config-dir "$PWD/data/letsencrypt" \
       --work-dir "$PWD/data/letsencrypt/work" \
       --logs-dir "$PWD/data/letsencrypt/logs" \
       --pre-hook "docker compose stop nginx" \
       --deploy-hook "docker compose restart nginx"
   ```

4. `./kp-msx.sh start`.
5. Renewal — cron. The hooks are stored inside the certificate, so a bare
   `renew` is enough; nginx is briefly stopped around the renewal and comes
   back with the new certificate:

   ```cron
   0 3 * * * cd /path/to/kp-msx && certbot renew --config-dir "$PWD/data/letsencrypt" --work-dir "$PWD/data/letsencrypt/work" --logs-dir "$PWD/data/letsencrypt/logs"
   ```

Notes:

- The certificate lives at `./data/letsencrypt/live/kp-msx/` (gitignored) and
  is mounted into nginx read-only; the private key never leaves the host.
- `SERVER_HOST`, the certificate's `-d` name and the domain the TV opens
  must be one and the same — this is exactly what keeps the player's media
  URLs same-origin and mixed-content-free.
- Moving to a different domain: re-run the command from step 3 with the new
  `-d` (same `--cert-name kp-msx`), update `SERVER_HOST`,
  `./kp-msx.sh restart`.

## Security

- The `id` query parameter is the device credential: anyone who knows it
  controls the linked KinoPub account. Keep URLs with `id=...` private. All
  traffic to the server is TLS-encrypted, so the ids cannot be sniffed or
  tampered with on the wire.
- `/msx/proxy` and `/msx/subtitle` are unauthenticated relays restricted to
  remembered KinoPub CDN domains (allowlist). Restrict access at the firewall
  level if that matters to you.
- CORS is wide open (`*`) because TV players require it — the device id is
  the only gate, treat it as a secret.
- `.env` holds the OAuth client credentials; device tokens live in the
  SQLite DB. Both are gitignored.

## Project Structure

```
src/                # App service: code + Dockerfile + requirements.txt (compose build context)
    main.py         # FastAPI app, middleware
    config/         # Settings (.env), constants
    routers/        # HTTP endpoints under /msx
    models/         # KinoPub API wrappers, Device, MSX rendering
    util/           # MSX JSON builders, proxy, SQLite
    pages/          # Self-hosted player plugins, helper pages
    icons/          # SVG icons (also served by nginx at /icons/)
conf/               # nginx config (HTTPS-only: app on 443, redirect on 80)
data/               # SQLite DB + letsencrypt (bind-mounted, gitignored)
backups/            # DB backups (gitignored)
kp-msx.sh           # Management script
cli/                # The 'admin' command tree executed by kp-msx.sh
docker-compose.yml  # server + nginx
```

## Acknowledgments

[slonopot/kp-msx](https://github.com/slonopot/kp-msx) ·
[Media Station X](https://msx.benzac.de/) ·
[msx-hlsx](https://github.com/slonopot/msx-hlsx)
