#!/bin/bash

useoc=false

usage()
{
  printf "\nfix-terminating.sh\n\n"
  echo "examples"
  echo "  # Use the oc client to fix my-project
  echo "  bash fix-terminating.sh -c my-project
  echo "  # Use certs to fix my-project
  echo "  bash fix-terminating.sh /path/to/ca.crt /path/to/admin.crt /path/to/admin.key https://cluster:443 my-project
  printf "\n"
}

while (( "$#" )); do
  case $1 in
    -c | --use-oc)             useoc=true
                               shift
                               namespace=$1
                               ;;
    -h | --help)               usage
                               exit 1
                               ;;
  esac
  shift
done

data="{\"apiVersion\":\"v1\",\"kind\":\"Namespace\",\"metadata\":{\"name\":\"${namespace}\"},\"spec\":{\"finalizers\":[]}}"

if [ "true" == "$useoc" ]
then
  printf "\nusing oc client. Ensure you are logged in\n terminating $namespace \n"
  token=$(oc whoami -t)
  clusterurl=$(oc whoami --show-server)

  curl -X PUT -H "Content-Type: application/json" \
    --data  ${data} \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $token" \
    ${clusterurl}/api/v1/namespaces/${namespace}/finalize
else
  clusterurl=$1
  namespace=$2
  cacert=${3:-/etc/origin/master/ca.crt}
  cert=${4:-/etc/origin/master/admin.crt}
  key=${5:-/etc/origin/master/admin.key}

  printf "\nusing certs\n"
  curl -X PUT -H "Content-Type: application/json" \
    --data  ${data} \
    -cacert ${cacert} \
    --cert ${cert} \
    --key ${key} \
    ${clusterurl}/api/v1/namespaces/${namespace}/finalize
fi
