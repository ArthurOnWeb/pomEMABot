FROM python:3.8-slim

# Avoid interactive prompts; make matplotlib headless
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    TZ=Europe/Paris

WORKDIR /app

# System deps (kept minimal). If you ever need compilers, add build-essential.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates tzdata \
 && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Create app user and own the app tree
RUN useradd -m app && chown -R app:app /app

# Copy entrypoint with perms/owner
COPY --chown=app:app --chmod=0755 docker/entrypoint.sh /entrypoint.sh

# Stay root here; entrypoint will chown /data and drop to 'app'
VOLUME ["/data"]

# No ports to expose (Telegram uses outbound connections)
CMD ["/entrypoint.sh"]
