#!/bin/bash

# Date: 04/18/2017
#
# Script Purpose: Create a bunch of PVs
# Version       : 1.0
#

set -o pipefail

if [ "$#" -ne 5 ]; then
    echo "

      Usage: create-pvs.sh NFS-Server NFS-ROOT-PATH VolumeSize SequenceStart SequenceEnd

      The following command 'create-pvs.sh nfs.moos.local /nfs/root/path 1 1 1'
      would create a PV with this json payload

      {
        \"apiVersion\": \"v1\",
        \"kind\": \"PersistentVolume\",
        \"metadata\": {
          \"name\": \"pv1g0001\"
        },
        \"spec\": {
          \"capacity\": {
            \"storage\": \"1Gi\"
          },
          \"accessModes\": [
            \"ReadWriteOnce\",
            \"ReadWriteMany\"
          ],
          \"nfs\": {
            \"path\": \"/nfs/root/path/pv1g0001\",
            \"server\": \"nfs.moos.local\"
          },
          \"persistentVolumeReclaimPolicy\": \"Recycle\"
        }
      }

    "
    exit 1
fi


nfs_server=$1
nfs_path=$2
vol_sz=$3
seq_start=$4
seq_end=$5

create_persistent_volume() {
  vol_nr=$1
  vol_size=$2
  nfs_server=$3
  nfs_path=$4
  #For example the PV name will be: pv1g0001
  vol_name="pv$2g$(printf %04d $1)"
  echo "Creating PV: ${vol_name}"

  # create persistent volume
if ! oc get -n default persistentvolumes pv${vol_nr} >/dev/null 2>&1; then
cat <<-EOF | oc create -n default -f -
  {
    "apiVersion": "v1",
    "kind": "PersistentVolume",
    "metadata": {
      "name": "${vol_name}"
    },
    "spec": {
      "capacity": {
        "storage": "${vol_size}Gi"
      },
      "accessModes": [
        "ReadWriteOnce",
        "ReadWriteMany"
      ],
      "nfs": {
        "path": "${nfs_path}/${vol_name}",
        "server": "${nfs_server}"
      },
      "persistentVolumeReclaimPolicy": "Recycle"
    }
  }
EOF
  else
    echo "ERROR: OpenShift persistent volume already exists. This seems wrong. Aborting."
    exit 1
  fi
}

# Check if executed as root
if [[ $EUID -ne 0 ]]; then
  echo "ERROR: This script must be run as root. Aborting."
  exit 1
fi

# Check if executed on OSE master
if ! systemctl status atomic-openshift-master-api >/dev/null 2>&1; then
  echo "ERROR: This script must be run on an OpenShift master. Aborting."
  exit 1
fi

for i in `seq ${seq_start} ${seq_end}`; do
  create_persistent_volume $i ${vol_sz} ${nfs_server} ${nfs_path}
done
