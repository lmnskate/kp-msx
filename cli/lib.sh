#!/usr/bin/env bash
# Shared helpers for the kp-msx.sh subcommand tree. Sourced by the command
# scripts in this directory, never executed directly.
KPMSX_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$KPMSX_ROOT"

compose() {
    docker compose "$@"
}

die() {
    echo "ERROR: $*" >&2
    exit 1
}

check_running() {
    if ! compose ps --status running --services 2>/dev/null | grep -qx server; then
        die "the stack is not running — start it with: ./kp-msx.sh start"
    fi
}

# Device management, executed by python inside the app container against the
# live SQLite file via util/db.py. Operation and device id come from sys.argv:
#   list | delete <id> | reset <id>
# Single-quoted for the shell, so the Python code must use double quotes only.
ADMIN_PY='
import sys

from util import db

op = sys.argv[1]

if op == "list":
    def settings_summary(raw):
        if raw is None:
            return "-"
        parts = []
        if raw.get("uhd"):
            parts.append("uhd")
        if raw.get("hdr"):
            parts.append("hdr")
        if raw.get("hevc"):
            parts.append("hevc")
        if raw.get("proxy"):
            parts.append("proxy")
        if raw.get("alternative_player"):
            parts.append("alt-player")
        if raw.get("poster_size") == "small":
            parts.append("posters=small")
        if raw.get("poster_proxy"):
            parts.append("poster-proxy")
        hidden = raw.get("menu_blacklist") or []
        if hidden:
            parts.append("menu=-" + ",-".join(sorted(hidden)))

        return " ".join(parts) if parts else "defaults"

    devices = db.list_devices()
    if not devices:
        print("No devices.")

        sys.exit(0)
    rows = []
    for device in devices:
        ua = device["user_agent"] or "-"
        if len(ua) > 50:
            ua = ua[:47] + "..."
        rows.append((
            device["id"],
            ua,
            "yes" if (device["refresh"] or device["token"]) else "no",
            settings_summary(device["settings"]),
        ))
    headers = ("ID", "USER-AGENT", "REGISTERED", "SETTINGS")
    widths = [
        max(len(str(value)) for value in column)
        for column in zip(headers, *rows)
    ]

    def line(columns):
        print("  ".join(
            str(value).ljust(width)
            for value, width in zip(columns, widths)
        ))

    line(headers)
    line(tuple("-" * width for width in widths))
    for row in rows:
        line(row)
else:
    device_id = sys.argv[2]
    if op == "delete":
        if db.delete_device(device_id) == 0:
            print(f"No such device: {device_id}")

            sys.exit(1)
        print(f"Deleted: {device_id}")
    elif op == "reset":
        if db.reset_device_settings(device_id) == 0:
            print(f"No such device: {device_id}")

            sys.exit(1)
        print(f"Settings reset: {device_id}")
    else:
        print(f"Unknown operation: {op}")

        sys.exit(1)
'
