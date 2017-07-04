#!/bin/bash

# Date: 04/18/2017
#
# Script Purpose: Returns the current status of the elasticsearch cluster.
# This script will only work on OCP 3.3 or earlier
# Version       : 1.0
#

if [ "$#" -lt 1 ]; then

  echo "
      Missing input parameters.

      Required Kibana Public URL

      Usage: elasticsearch-health-check-33.sh [Kibana Public URL] [OCP Token]

      Example:  ./elasticsearch-health-check-33.sh https://kibana.moos.local djafksdljasdkl;fjads;klfjakls;dfj;kladsjfldksa;

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

#Check the passed in token and validate.  If failure occurs, stop.
whoami=`oc whoami -t`
if [[ "$whoami" != "$token" ]]; then
  echo "==================================
Script failed token validation!
Check the OCP URL and token.
=================================="
  exit 1
fi

cluster_status_string=`curl -s --insecure -H "Authorization: Bearer ${token}" -XGET "${public_url}/elasticsearch/_cat/health"`
if [ -z "$cluster_status_string" ]; then

  echo "=====================================================================
cURL returned: ${cluster_status_string}.
====================================================================="
  exit 1

fi

cluster_color=`echo -n "${cluster_status_string}" | awk '{print $4}' `
echo "Cluster Color: ${cluster_color}"

if [ "$cluster_color" = "green" ]; then
  exit 0
else
  exit 1
fi
