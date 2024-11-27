#!/bin/bash

# création du répertoire
dest="./data"
mkdir -p $dest

# l (do_login), d (do_dryrun), p (pattern), t (destination en local), s (source sur azure), g (glob file)
./01_fetchFiles.sh -p "nlp_data/*.csv" -t $dest -s data -g nlp_data.json
./01_fetchFiles.sh -p "machine_learning/*.zip" -t $dest -s data -g machine_learning.json
./01_fetchFiles.sh -p "product_eval/*.parquet" -t $dest -s data -g product_eval.json

# ETL
./02_parquetFlow.py # On peut ajouter un paramètre 1 pour ne pas créer les images