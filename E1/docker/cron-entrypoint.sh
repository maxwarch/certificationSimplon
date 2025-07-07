#!/bin/bash

chmod u=r,go=r -R /app/refresh_cron.py
chmod u=r,go=r,a+x -R /app/refresh_cron.py

printenv > /etc/environment
cron -f -l 2 -L /dev/stdout