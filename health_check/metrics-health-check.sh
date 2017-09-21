#!/bin/bash

# Date: 04/18/2017
#
# Script Purpose: Perform a real health check of the metrics service.
# Version       : 1.0
#


if [ "$#" -lt 1 ]; then
    echo "

      Description:  This script will actually pull Hawkular stats for an
      OpenShift system pod.  If the call does not return stats, then we
      safely assume the service is down.

      Usage: metrics-health-check.sh [Public URL] [OCP Token]

      Example: metrics-health-check.sh https://hawkular-metrics-openshift-infra.ose34.moos.local asdfsdfasdf8asdifa90sd890fas8df0

      If token is not provided, the script will execute oc whoami -t to get token.

      Requires:  cURL, and oc tools if token is not specified.

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

#Globals
#This is the pod for which metrics will be quried.
#If metrics exist, this pod will exist.
readonly POD_LABEL="hawkular-cassandra"
#Metrics OCP Namespace, this is constant
readonly POD_NAMESPACE="openshift-infra"
#Two connection parameters, these may need to be tweaked
#Depending on what defines a dead service.
readonly MAX_TIME="30"
readonly CONNECT_TIMEOUT="1"

#cURL parms and headers
#parms passed to cURL
curl_parms="-sk --max-time ${MAX_TIME} --connect-timeout ${CONNECT_TIMEOUT}"
#URL to cURL
url="${public_url}/hawkular/metrics/counters/data?stacked=true&tags=descriptor_name:cpu%2Frx,type:pod,labels:%5E%28%3F%3D.%2A%5Cbmetrics-infra%3A${POD_LABEL}%5Cb%29.%2A%24&bucketDuration=60000ms&start=-2mn"
#Required, Hawkular-Tenant header.
tenant_header="Hawkular-Tenant: ${POD_NAMESPACE}"
#Required, auth token.
token_header="Authorization: Bearer ${token}"
#Not required, just included
accept_header="Accept: application/json"
#Not required, but included for logging.
agent_header="User-Agent: metrics-health-check.sh"
#Required to get cURL to return just the HTTP status code, i.e. 200
output="-o /dev/null"
http_reg="%{http_code}"

#Uncomment to debug
#echo "cURL url: " ${url}
#echo "tenant: ${tenant_header}"
#echo "token:  ${token_header}"
#echo "accept: ${accept_header}"
#echo "agent:  ${agent_header}"

#Perform the cURL, and store the results.
#Anything non 200 specifies an error.
http_resp_code=`curl ${curl_parms} "${url}" \
 -H "${token_header}" \
 -H "${tenant_header}" \
 -H "${accept_header}" \
 -H "${agent_header}" \
 ${output} -w "${http_reg}" `

#Echo the response
echo "Server Responded with HTTP Code: $http_resp_code"

#Perform check and return 0 or -1
if [ "$http_resp_code" = "200" ]; then
  echo "Ok"
  exit 0
else
  echo "Error"
  exit 1
fi
