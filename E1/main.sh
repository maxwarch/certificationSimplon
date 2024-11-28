#!/bin/bash

# création des répertoires data et tmp
dest="./data"
tmp="./tmp"
mkdir -p $dest
mkdir -p $tmp
tmp_fullpath=$(readlink -f $tmp)

do_dryrun=0

while getopts ":d:" opt; do
  case $opt in
    d)
      do_dryrun="$OPTARG"
      ;;
    \?)
      echo "Option invalide: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG nécessite un argument." >&2
      exit 1
      ;;
  esac
done

# l (do_login), d (do_dryrun), p (pattern), t (destination en local), s (source sur azure), g (glob file)
./01_fetchFiles.sh -p "nlp_data/*.csv" -t $dest -s data -g nlp_data.json -d $do_dryrun
./01_fetchFiles.sh -p "machine_learning/*.zip" -t $dest -s data -g machine_learning.json -d $do_dryrun
./01_fetchFiles.sh -p "product_eval/*.parquet" -t $dest -s data -g product_eval.json -d $do_dryrun

# ETL
## Process des fichiers .parquet. Création des images et d'un fichier .csv
./02_parquetFlow.py # On peut ajouter un paramètre 1 pour ne pas créer les images

cd data/machine_learning && \
  unzip -o reviews.zip amazon_review_polarity_csv.tgz && \
  tar -xvf amazon_review_polarity_csv.tgz && \
  rm -vf amazon_review_polarity_csv.tgz && \
  mv reviews.zip $tmp_fullpath && \
  cd ../..