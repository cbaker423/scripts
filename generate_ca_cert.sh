#!/bin/bash

COUNTRY="US"
STATE="Texas"
LOCALITY="Austin"
ORGANIZATION="IBM"
COMMON_NAME="127.0.0.1"
DEFAULT_MESSAGE="Country=$COUNTRY\nState=$STATE\nLocality=$LOCALITY\nOrganization=$ORGANIZATION\nCommon Name=$COMMON_NAME"
HELP_MESSAGE="USAGE: ./generate_ca_cert.sh [options]\n
\n
This script will generate a CA cert and a private key\n
Add the CA cert to the trusted root CAs\n
\n
Options:\n
  -h, --help           \tDisplay this help message and exit\n
  -d, --defaults       \tDisplay the default subject values and exit\n
  -C, --country        \tCountry subject to use when creating the CA cert (ex. US)\n
  -s, --state          \tState subject to use when creating the CA cert (ex. Texas)\n
  -l, --locality       \tLocality to use for CA cert (ex. City)\n
  -o, --organization   \tOrganization to use for CA cert (ex. IBM)\n
  -c, --common-name    \tCommon name to use for CA cert (ex. FQDN or IP addr)\n
"

if [[ $# -lt 1 ]]; then
    echo -e $HELP_MESSAGE
    echo -e "\n\nWoud you like to create a CA cert with the default subject line? (yes/no)"
    read choice
    if [[ $choice == "no" ]] || [[ $choice == "NO" ]]; then
        exit
    fi
fi
    

for i in "$@"; do
case $i in
    -h|--help)
    echo -e $HELP_MESSAGE
    exit
    ;;
    -d|--defaults)
    echo -e $DEFAULT_MESSAGE
    exit
    ;;
    -C=*|--country=*)
    COUNTRY="${i#*=}"
    shift
    ;;
    -s=*|--state=*)
    STATE="${i#*=}"
    shift
    ;;
    -l=*|--locality=*)
    LOCALITY="${i#*=}"
    shift
    ;;
    -o=*|--organization=*)
    ORGANIZATION="${i#*=}"
    shift
    ;;
    -c=*|--common-name=*)
    COMMON_NAME="${i#*=}"
    shift
    ;;
    *)
    echo -e "Unrecognized Arguments...exiting"
    exit
    ;;
esac
done

openssl req -nodes -newkey rsa:2048 -keyout data_protect.key -out data_protect_ca.crt -x509 -days 365 -config openssl.cnf -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORGANIZATION/CN=$COMMON_NAME"
