#!/bin/bash

# date +%s: Obtient le nombre de secondes depuis l'Epoch.
# $(...) + 1800: Ajoute 1800 secondes (30 minutes).
# date -u -r ...: Utilise -r pour indiquer que l'argument est un timestamp Epoch et -u pour UTC.
# '+%Y-%m-%dT%H:%MZ': Formatte la date au format ISO 8601.

end=`date -u -r $(($(date +%s) + 1800)) '+%Y-%m-%dT%H:%MZ'` 
az storage blob generate-sas \
    --account-name datalakedeviavals \
    --name data \
    --permissions w \
    --expiry $end \
    --auth-mode login \
    --as-user \
    --https-only \
    --blob-url https://datalakedeviavals.blob.core.windows.net/