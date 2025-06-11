#! /bin/zsh -

# https://learn.microsoft.com/en-us/rest/api/storageservices/create-user-delegation-sas

if [ -z "$RUNNING_IN_DOCKER" ] ; then
  source .env
fi

#echo "$@"
# options courtes : l (do_login), d (do_dryrun), p (pattern), t (destination), s (source), g (glob)
# options longues : do_login, do_dryrun, pattern, destination, source, glob
while getopts ":l:d:p:t:s:g:" opt; do
  case $opt in
    l)
      do_login="$OPTARG"
      ;;
    d)
      do_dryrun="$OPTARG"
      ;;
    p)
      pattern="$OPTARG"
      ;;
    t)
      destination="$OPTARG"
      ;;
    s)
      source="$OPTARG"
      ;;
    g)
      glob="$OPTARG"
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

if [ -z "$pattern" ]; then
  echo "Erreur: L'option -p <pattern> est obligatoire."
  echo "Utilisation: $0 -p product_eval/*.parquet"
  exit 1
fi

shift $((OPTIND-1)) # supprimer les options des arguments positionnels
echo $do_login
if [[ "$do_login" == "true" || "$do_login" == "1" ]]; then
  print -P "%F{green}%  Connexion en cours... %f"
  yes | az login --use-device-code
else
  output=$(az account show)
  if [[ ! -z "$output" && "$output"=~"environmentName" ]]; then
    echo "Déjà connecté."
  else
    print -P "%F{red}%  Non connecté à Azure. %f"
    print -P "%F{green}%  Connexion en cours... %f"
    yes | az login --use-device-code
  fi
fi

az configure --defaults group=$RESSOURCE_GROUP

conn_string=$(az storage account show-connection-string --name $ACCOUNT_NAME --output tsv)
# echo $conn_string

if [[ "$do_dryrun" == "true" || "$do_dryrun" == "1" ]]; then
  print -P "%F{green}%  **** dry run  $glob **** %f"
  result=$(az storage blob download-batch \
      --destination $destination \
      --source $source \
      --connection-string $conn_string \
      --pattern "$pattern" \
      --overwrite true \
      --max-connections 4 \
      --output json \
      --dryrun)
else
  print -P "%F{green}%  **** fetch $glob **** %f"
  az storage blob download-batch \
      --destination $destination \
      --source $source \
      --connection-string $conn_string \
      --pattern "$pattern" \
      --overwrite true \
      --max-connections 4 \
      --output json \
      > "$destination/$glob"
fi