FROM python:3.11-slim-bookworm

WORKDIR /app

# Installation des dépendances en une seule étape pour réduire la taille de l'image
RUN apt-get update && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/* \
    && touch /var/log/cron.log

# Copier les fichiers nécessaires
RUN ln -s /usr/local/bin/python /usr/bin/python

COPY . .
COPY crontab /etc/cron.d/cronjob
COPY docker/cron-entrypoint.sh /tmp/cron-entrypoint.sh

# Installation des dépendances Python
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Configuration de cron
RUN chmod 0644 /etc/cron.d/cronjob \
    && crontab /etc/cron.d/cronjob \
    && chmod +x /tmp/cron-entrypoint.sh

# Définir le chemin Python
ENV PYTHONPATH="${PYTHONPATH}:/app/"
ENV PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s CMD pgrep cron || exit 1

CMD ["/bin/bash", "/tmp/cron-entrypoint.sh"]
