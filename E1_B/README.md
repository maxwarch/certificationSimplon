### Construction + démarrage
`./start.sh`

A la suite du démarrage du conteneur, un terminal zsh s'ouvre depuis le conteneur.

Démarrer la récupération des doc : `./main.sh`

### Arrêt
`docker stop e1-app-1`

### Stats
`docker stats`

### Pour tester
`./01_fetchFiles.sh -p "nlp_data/*.csv" -t ./data -s data -g nlp_data.json -l true`

### Commandes utiles

récupérer la version du système dans Docker
`cat /etc/os-release`

cron

`service cron start | reload | stop`

`tail -f /var/log/cron.log`

https://zippy-twig-11a.notion.site/Brief-Extraction-de-donn-es-multi-sources-annexe-E1-1451f9041c96805d9e06f5db6bf40fbf