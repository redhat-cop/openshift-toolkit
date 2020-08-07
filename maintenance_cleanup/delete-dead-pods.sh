#!/bin/bash

# Date: 04/18/2017
#
# Script Purpose: Cleanup completed or dead pods
# Version       : 1.0
#


if [ "$#" -gt 1 ]; then
    echo "

      Usage: delete-dead-pods.sh [Dry Run]

      Example: delete-dead-pods.sh false

      NOTE: If not specified, Dry Run is assumed true.
    "

    exit 1
fi

dryrun=true
if [ "$#" -gt 0 ]; then
    dryrun=$1
fi

if [ "$dryrun" = "true" ]; then
  echo "Executing dry run"

  #Just echo the namespace and pod.
  oc get pods --all-namespaces --no-headers | awk '$4 == "Error" \
    || $4 == "Completed" \
    || $4 == "DeadlineExceeded" \
    || $4 == "ContainerCannotRun" \
    || $4 == "Terminating" \
    {system("bash -c '\''echo namespace: "$1", pod: "$2" '\''")}'

  exit 0
fi

if [ "$dryrun" = "false" ]; then
  echo "Executing actual delete"

  #Delete all Error, Completed, DeadlineExceeded, or ContainerCannotRun pods.
  oc get pods --all-namespaces --no-headers | awk '$4 == "Error" \
    || $4 == "Completed" \
    || $4 == "DeadlineExceeded" \
    || $4 == "ContainerCannotRun" \
    {system("bash -c '\''oc delete pod -n "$1" "$2" '\''")}'

  #Force kill any hanging pods
  oc get pods --all-namespaces --no-headers | awk '$4 == "Terminating" \
    {system("bash -c '\''oc delete pod -n "$1" "$2" --force --grace-period=0 '\''")}'

  exit 0
fi

echo "Invalid command: $dryrun"
exit 1
