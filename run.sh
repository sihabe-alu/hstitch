#!/bin/sh
cd "$(dirname "$0")"
. .venv/bin/activate
exec flask --app app run --host "$(tailscale ip -4 | head -1)" --port 5000
