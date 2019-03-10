#!/bin/bash

# Date: 30/09/2018
#
# Script Purpose: Performs a backup of etcd v3 data (snapshot) and config (/etc/etcd/), when etcd running in static Pods (since OCP 3.10).
#                 Manages backup retention, It also deletes old backup files.
# Version       : 1.0
#

set -euo pipefail

# Check proper inputs
usage(){
  echo "Backup etcd data (snapshot) and config (/etc/etcd). Creates a tar.gz and save it in a different folder."
  echo "Also manages backup retention."
  echo ""
  echo "Usage:"
  echo "  $0 dest_folder [retention_days]"
  echo ""
  echo "Options:"
  echo "  dest_folder: Destination folder where to save the backup"
  echo "  [retention_days]: Optional, number of retention days for backup files. Default 30."
  echo ""
  echo "Examples:"
  echo "  # Backup etcd node."
  echo "  $0 /tmp"
  echo ""
  echo "  # Backup etcd node. Retain last 15 days o backup files."
  echo "  $0 /tmp 15"
  echo ""
  exit 1
}

if [[ $# -lt 1 ]]
then
  usage
fi

# Vars
HOSTNAME=$(hostnamectl --static)
TS=$(date +"%Y%m%d-%H%M%S")

MASTER_EXEC="/usr/local/bin/master-exec"
ETCD_POD_MANIFEST="/etc/origin/node/pods/etcd.yaml"

ETCD_BCK_DIR="${1}"
ETCD_DATA_BCK_DIR="etcd_data_bck.${TS}"

ETCD_CONFIG_DIR="/etc/etcd"
ETCD_CONFIG_BCK_DIR="etcd_config_bck.${TS}"

ETCD_FINAL_BCK_FILE="etcd_bck.${HOSTNAME}.${TS}.tar.gz"

RETENTION_DAYS=${2-30}

log(){
  date "+%F %T: ${@}"
}

die(){
  log "$1"
  exit "$2"
}

## Pre checks
# Check if the second arg is a number
[[ ! ${RETENTION_DAYS} == ?(-)+([0-9]) ]] \
  && die "Invalid input, is not an integer." 1

# Check the output dir exists
[ ! -d "${ETCD_BCK_DIR}" ] \
  && die "Invalid output directory, It doesn't exist." 1

# Check master-exec
[ -z "${MASTER_EXEC}" ] \
  && die "${MASTER_EXEC} not found" 1

# Check master-exec
[ -z "${ETCD_POD_MANIFEST}" ] \
  && die "${ETCD_POD_MANIFEST} not found" 1

# Check if the backup destination folder is not full > 95%
USAGE_THRESHOLD=95
USAGE=$(df -h "${ETCD_BCK_DIR}" | grep -v 'Filesystem' | awk '{ print $5}' | cut -d '%' -f 1)
[ "$USAGE" -gt "$USAGE_THRESHOLD" ] \
  && die "${ETCD_BCK_DIR} is almost full ${USAGE}% > ${USAGE_THRESHOLD}%, aborting backup" 1


backup_config() {
  log "Backing up ETCD config."
  cp -a "${ETCD_CONFIG_DIR}" "/tmp/${ETCD_CONFIG_BCK_DIR}"
}

backup_data() {

  log "Backing up ETCD data, performing snapshot."
  # etcd endpoint 
  ETCD_EP=$(grep https ${ETCD_POD_MANIFEST} | cut -d '/' -f3)

  # snapshot output is /var/lib/etcd/ because is mounted from the host, and we can move it later to another host folder.
  # > /usr/local/bin/master-exec etcd etcd /bin/bash -c "ETCDCTL_API=3 /usr/bin/etcdctl \
  # --cert /etc/etcd/peer.crt --key /etc/etcd/peer.key --cacert /etc/etcd/ca.crt --endpoints ${ETCD_EP} snapshot save /var/lib/etcd/snapshot.db"
  ${MASTER_EXEC} etcd etcd /bin/bash -c "ETCDCTL_API=3 /usr/bin/etcdctl \
  --cert /etc/etcd/peer.crt --key /etc/etcd/peer.key --cacert /etc/etcd/ca.crt \
  --endpoints ${ETCD_EP} snapshot save /var/lib/etcd/snapshot.db"

  log "Backing up ETCD data, validating snapshot."
  # Validate the status of the snapshot
  # > snapshot status /var/lib/etcd/snapshot.db 
  ${MASTER_EXEC} etcd etcd /bin/bash -c "ETCDCTL_API=3 /usr/bin/etcdctl \
  --cert /etc/etcd/peer.crt --key /etc/etcd/peer.key --cacert /etc/etcd/ca.crt \
  --endpoints ${ETCD_EP} snapshot status /var/lib/etcd/snapshot.db"

   # Check the etcd snapshot
  [ "$?" -ne 0 ] \
    && die "/var/lib/etcd/snapshot.db is not a valid etcd backup. Please check the status of your etcd cluster" 1

  # Move the snapshot to the temp bck dir.
  mv /var/lib/etcd/snapshot.db /tmp/${ETCD_DATA_BCK_DIR}/snapshot.db
}

backup(){
  log "Backing up ETCD."
  mkdir -p /tmp/${ETCD_DATA_BCK_DIR}/

  backup_config
  backup_data

  log "Creating tar.gz file"
  tar cvfz "${ETCD_BCK_DIR}/${ETCD_FINAL_BCK_FILE}" --directory /tmp "${ETCD_CONFIG_BCK_DIR}" "${ETCD_DATA_BCK_DIR}"

  log "Check your backup file on: ${ETCD_BCK_DIR}/${ETCD_FINAL_BCK_FILE}"

  log "Deleting temporary files"
  rm -rf "/tmp/${ETCD_CONFIG_BCK_DIR}" "/tmp/${ETCD_DATA_BCK_DIR}"
}

# Keep the last #RETENTION_DAYS files
purge_old_backups(){
  log "Deleting old backup files...Keeping the last ${RETENTION_DAYS} days"
  find "${ETCD_BCK_DIR}"/etcd_bck* -type f -mtime +"${RETENTION_DAYS}"
  find "${ETCD_BCK_DIR}"/etcd_bck* -type f -mtime +"${RETENTION_DAYS}" -delete
}

backup
purge_old_backups

exit 0
