#!/bin/bash

# création du répertoire
dest="./data"
mkdir -p $dest

./01_fetchFiles.sh -p "nlp_data/*.csv" -t $dest -s data -g nlp_data.json
./01_fetchFiles.sh -p "machine_learning/*.zip" -t $dest -s data -g machine_learning.json
./01_fetchFiles.sh -p "product_eval/*.parquet" -t $dest -s data -g product_eval.json