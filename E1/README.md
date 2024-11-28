### Building and running your application

When you're ready, start your application by running:

`docker compose up -d --build`

### Lancement du terminal Docker
`docker exec -it e1-app-1 /bin/zsh`

### Arrêt
`docker stop e1-app-1`

### Stats
`docker stats`

### Pour tester
`./01_fetchFiles.sh -p "nlp_data/*.csv" -t ./data -s data -g nlp_data.json -l true`

### Commandes utiles

récupérer la version du système dans Docker
`cat /etc/os-release`