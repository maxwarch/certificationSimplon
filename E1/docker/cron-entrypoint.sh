#!/bin/bash

chmod u=r,go=r /app/refresh_cron.py
chmod u=r,go=r,a+x /app/refresh_cron.py

printenv > /etc/environment
cron -f -l 2 -L /dev/stdout