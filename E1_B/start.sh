#!/bin/bash

docker compose up -d --build
docker exec -it e1-app-1 /bin/zsh