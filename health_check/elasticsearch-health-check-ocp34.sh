#!/bin/bash

# Date: 04/25/2017
#
# Script Purpose: Returns the current status of the elasticsearch cluster.
# This script will only work on OCP 3.4 or later
# Version       : 1.0
#

if [ "$#" -lt 1 ]; then

  echo "
      Missing input parameters.

      Required Kibana Public URL

      Usage: elasticsearch-health-check-34.sh [Kibana Public URL] [OCP Token]

      Example:  ./elasticsearch-health-check-34.sh https://kibana.moos.local djafksdljasdkl;fjads;klfjakls;dfj;kladsjfldksa;

      User token can be retrieved by running 'oc whoami -t'
  "
  exit 1
fi

public_url=$1

#if user supplied token then use it, else get it from CLI
if [ "$#" -eq 2 ]; then
  token=$2
else
  token=`oc whoami -t`
fi

cluster_color=`curl -sk "${public_url}/api/status" \
  -H "Accept-Encoding: gzip, deflate, sdch, br" \
  -H "Accept-Language: en-US,en;q=0.8" \
  -H "Accept: application/json" \
  -H "User-Agent: health-checker" \
  -H "Authorization: Bearer $(oc whoami -t)" \
  -H "Connection: keep-alive" --compressed | \
  python -c 'import sys, json; print json.dumps(json.load(sys.stdin)["status"]["overall"]["state"], sort_keys=True, indent=4)'`


echo "Cluster is ${cluster_color}"

if [ "$cluster_color" = "\"red\"" ]; then

  exit 1

fi

exit 0
