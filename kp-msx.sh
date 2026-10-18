#!/usr/bin/env bash
#
# kp-msx.sh — manage the KP-MSX Docker deployment.
#
# Usage: ./kp-msx.sh <command>
#
#   install                Build/pull the images and prepare the data dirs.
#                          Creates .env from .env.example if missing — edit it!
#   start                  Start the stack (requires: install)
#   stop                   Stop and remove the containers (data in ./data is kept)
#   restart                Recreate the containers, re-reading .env and compose config
#   backup                 Back up the database into ./backups/ (safe on a live DB)
#   admin ...              Device management — a command tree of its own:
#                          './kp-msx.sh admin' lists its commands and their help
#   help                   Show this help

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
cd "$ROOT_DIR"

compose() {
    docker compose "$@"
}

check_env() {
    if [ ! -f .env ]; then
        echo "ERROR: .env not found." >&2
        echo "Create it first:  ./kp-msx.sh install  (generates one to edit)" >&2
        exit 1
    fi
}

check_installed() {
    if ! docker image inspect kp-msx-server:latest >/dev/null 2>&1; then
        echo "ERROR: the app image is not built yet." >&2
        echo "Run:  ./kp-msx.sh install" >&2
        exit 1
    fi
}

check_running() {
    if ! compose ps --status running --services 2>/dev/null | grep -qx server; then
        echo "ERROR: the stack is not running." >&2
        echo "Start it with:  ./kp-msx.sh start" >&2
        exit 1
    fi
}

# Directories bind-mounted into containers must exist beforehand and be
# writable by uid 1000 (the container user). When Docker creates them itself
# they end up owned by root, and the app then dies at startup with a SQLite
# "readonly database" error — so fix the ownership right here when we can.
ensure_mount_dirs() {
    for dir in data backups; do
        mkdir -p "$dir"
        if [ "$(id -u)" = "0" ]; then
            [ "$(stat -c '%u' "$dir")" = "1000" ] || chown -R 1000:1000 "$dir"
        elif [ "$(stat -c '%u' "$dir" 2>/dev/null)" != "1000" ] || [ ! -w "$dir" ]; then
            echo "NOTE: ./$dir must be writable by uid 1000 (the container user)." >&2
            echo "      Fix with:  sudo chown -R 1000:1000 $dir" >&2
        fi
    done
}

cmd_install() {
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "WARNING: .env did not exist — created it from .env.example."
        echo "         EDIT .env BEFORE STARTING THE STACK: set at least"
        echo "         SERVER_HOST, KP_CLIENT_ID, KP_CLIENT_SECRET."
        echo
    fi
    ensure_mount_dirs
    compose build
    echo
    echo "Installed. Edit .env if you have not yet, then start:  ./kp-msx.sh start"
}

cmd_start() {
    check_env
    ensure_mount_dirs
    check_installed
    compose up -d
    echo "KP-MSX is starting."
}

cmd_stop() {
    compose down
}

cmd_restart() {
    check_env
    ensure_mount_dirs
    check_installed
    compose down
    compose up -d
}

cmd_backup() {
    mkdir -p backups
    file="kp-sqlite-$(date +%Y%m%d-%H%M%S).db"

    if compose ps --status running --services 2>/dev/null | grep -qx server; then
        # A live DB must not be copied raw — use SQLite's online backup API
        compose exec -T server python -c "
import sqlite3
source = sqlite3.connect('/data/kp-sqlite.db')
target = sqlite3.connect('/backups/$file')
source.backup(target)
target.close()
source.close()
"
    elif [ -f data/kp-sqlite.db ]; then
        cp data/kp-sqlite.db "backups/$file"
    else
        echo "ERROR: no database found to back up." >&2
        exit 1
    fi

    echo "Backup saved: backups/$file"
}

cmd_help() {
    awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"
}

case "${1:-help}" in
    install) cmd_install ;;
    start)   cmd_start ;;
    stop)    cmd_stop ;;
    restart) cmd_restart ;;
    backup)  cmd_backup ;;
    admin)   shift; exec "$ROOT_DIR/cli/admin" "$@" ;;
    help|-h|--help) cmd_help ;;
    *)
        echo "Unknown command: $1" >&2
        cmd_help >&2
        exit 1
        ;;
esac
