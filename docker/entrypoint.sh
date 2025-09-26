#!/usr/bin/env bash
set -euo pipefail

# Ensure /data exists and is owned by app (named volume comes in as root)
mkdir -p /data
chown -R app:app /data || true

# Create the DB file if missing, with correct owner
if [ ! -f /data/ema_bot.db ]; then
  install -o app -g app -m 0644 /dev/null /data/ema_bot.db
fi

# Symlink into /app so your code sees ema_bot.db next to main.py
if [ ! -e /app/ema_bot.db ]; then
  ln -s /data/ema_bot.db /app/ema_bot.db
fi

# Drop privileges and launch the bot
exec su -s /bin/sh -c "cd /app && exec python main.py" app
