#!/bin/bash

# Date: 04/18/2017
#
# Script Purpose: Performs a backup of the certificates on the current master node.
# Version       : 1.0
#

#Directory that will be backed up on each master
readonly SOURCE_BACKUP_DIR="/etc/origin/master"
#Prefix of the generated tar.gz file
readonly TAR_FILE_PREFIX="certs-and-keys"
#Temporary location where the tar file will be created.  This file will be removed.
readonly DEST_BACKUP_DIR="/tmp"
#Location (on the master) where the tar will be copied.
#This parameter should be updated to use a location that's backed up on the host.
readonly BACKUP_DEST_DIR="/tmp/ocp-master-backup"

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

#Variable to hold path to tar
base_file="${DEST_BACKUP_DIR}/${TAR_FILE_PREFIX}-$HOSTNAME-$(date -u '+%Y%m%d-%k%M%S')"
tar_name="${base_file}.tar"
gz_name="${base_file}.tar.gz"

#cd into the dir to backup
cd ${SOURCE_BACKUP_DIR}

#tar the .crt files
echo "Adding all .crt files from ${SOURCE_BACKUP_DIR}"
tar cf ${tar_name} *.crt

#tar the key files
echo "Adding all .key files from ${SOURCE_BACKUP_DIR}"
tar rf ${tar_name} *.key

#Compress the tar
echo "Compressing tar file: ${tar_name}"
gzip "${tar_name}"

#make sure the backup dir exists.
mkdir -p ${BACKUP_DEST_DIR}

#move the tar.gz to the backup location
echo "Moving: ${gz_name} to: ${BACKUP_DEST_DIR}"
mv ${gz_name} ${BACKUP_DEST_DIR}

echo "Great Success"
