#!/bin/bash

clusterurl=$1
namespace=$2
cacert=${3:-/etc/origin/master/ca.crt}
cert=${4:-/etc/origin/master/admin.crt}
key=${5:-/etc/origin/master/admin.key}

curl -X PUT \
     --data "{\"apiVersion\":\"v1\",\"kind\":\"Namespace\",\"metadata\":{\"name\":\"${namespace}\"},\"spec\":{\"finalizers\":[]}}" \
     -H "Content-Type: application/json" \
     -cacert ${cacert} \
     --cert ${cert} \
     --key ${key} \
     ${clusterurl}/api/v1/namespaces/${namespace}/finalize

