#!/bin/bash

# Date: 04/19/2017
#
# Script Purpose: Cleanup replication controllers
# This is a massive cleanup script that will remove all RC and deployments
# that have an RC count of 0.
#
# Version       : 1.0
#

if [ "$#" -gt 1 ]; then
    echo "

      Usage: delete-expired-replicaiton-controllers.sh [Dry Run]

      Example: delete-expired-replicaiton-controllers.sh false

      NOTE: If not specified, Dry Run is assumed true.
    "

    exit 1
fi

#Globals
MAX_DAYS=60

dryrun=true
if [ "$#" -gt 0 ]; then
    dryrun=$1
fi

if [ "$dryrun" = "true" ]; then
  echo "Executing dry run"

  #Just echo the name
  oc get rc --all-namespaces --no-headers | \
    awk '$3 == 0 && \
    $4 == 0 && \
    $5 == 0 && \
    int(substr($6, 1, length($6) - 1 )) > 30 \
    {system("bash -c '\''echo namespace: "$1", dc: "$2", desired: "$3", curr: "$4", age: "$6" '\''")}'

  exit 0
fi

if [ "$dryrun" = "false" ]; then
  echo "Executing actual delete"

  #Delete all RC with a count of 0
  oc get rc --all-namespaces --no-headers | \
    awk '$3 == 0 && \
    $4 == 0 && \
    $5 == 0 && \
    int(substr($6, 1, length($6) - 1 )) > 30 \
    {system("bash -c '\''oc delete rc -n "$1" "$2"'\''")}'

  exit 0
fi

echo "Invalid command: $dryrun"
exit 1
