### Building and running your application

When you're ready, start your application by running:

`docker compose up -d --build`

`docker compose up -d`

`docker exec -it e1-app-1 /bin/zsh`

### Pour tester
`./01_fetchFiles.sh -p "nlp_data/*.csv" -t ./data -s data -g nlp_data.json -l true`