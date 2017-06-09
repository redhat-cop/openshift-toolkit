#!/bin/bash

# Date: 04/19/2017
#
# Script Purpose: Create a backup of etcd.  Must be run on a master node.
# Version       : 2.0 (Automatically query and get list of masters)
#

#Directory that will be backed up on each master
readonly ETC_DIR="/var/lib/etcd"
#Temporary location where the etc directory will be backed up.  This dir will be removed.
readonly ETC_BACKUP_DIR="/tmp/etcd.bak"
#Prefix of the generated tar.gz file
readonly TAR_FILE_PREFIX="etcd"
#Temporary location where the tar file will be created.  This file will be removed.
readonly DEST_BACKUP_DIR="/tmp"
#Location (on the Ansible host) where the tar will be copied.
readonly HOST_DEST_DIR="/tmp"

#######################################
# Stops the etcd service on the specified master
# Globals:
#   None
# Arguments:
#   OCP Master FQDN - $1
# Returns:
#   None
#######################################
stop_etcd() {
  echo "Stopping etcd on host: $1"
  ssh $1 "systemctl stop etcd"
  #Create a list of masters
  MASTERS_LIST+="https://${1}:2379,"
}

#######################################
# Starts the etcd service on the specified master
# Globals:
#   None
# Arguments:
#   OCP Master FQDN - $1
# Returns:
#   None
#######################################
start_etcd() {
  echo "Starting etcd on host: $1"
  ssh $1 "systemctl start etcd"
}



#######################################
# Back up the current masters etcd
# Globals:
#   ETC_BACKUP_DIR
#   ETC_DIR
#   DEST_BACKUP_DIR
#   TAR_FILE_PREFIX
# Arguments:
#   None
# Returns:
#   None
#######################################
backup_master_etcd() {

  #Remove tmp backup etcd dir
  rm -rf ${ETC_BACKUP_DIR}

  # Backup etcd on the master
  echo "Backing up etcd: ${ETC_DIR} to ${ETC_BACKUP_DIR}"
  etcdctl backup --data-dir ${ETC_DIR} --backup-dir ${ETC_BACKUP_DIR}

  #Tar etcd backup on master
  tar_file_name="${DEST_BACKUP_DIR}/${TAR_FILE_PREFIX}-$HOSTNAME-$( date -u '+%Y%m%d-%k%M%S').tar.gz"
  echo "Creating tar: ${tar_file_name} of etc backup: ${ETC_BACKUP_DIR}"
  cd ${ETC_BACKUP_DIR} && tar czf ${tar_file_name} .

  #Remove tmp etcd backup dir on each master
  echo "Removing etcd backup dir: ${ETC_BACKUP_DIR}"
  rm -rf "${ETC_BACKUP_DIR}"

  #Move the tar from the local to archive directory.
  echo "Moving tar: ${tar_file_name} to ${HOST_DEST_DIR}"
  mv ${tar_file_name} "${HOST_DEST_DIR}"
}

#################Code Exectuion Starts Here#################

# Check if executed as root
if [[ $EUID -ne 0 ]]; then
  echo "ERROR: This script must be run as root. Aborting."
  exit 0
fi

# Check if executed on OSE master
if ! systemctl status atomic-openshift-master-api >/dev/null 2>&1; then
  echo "ERROR: This script must be run on an OpenShift master. Aborting."
  exit 0
fi

login_result=`oc login -u system:admin`
if [[ "$login_result" == *"Login failed"* ]]; then
  echo "==================================
Login failed!
=================================="
  exit 1
fi

#Check the passed in token and validate.  If failure occurs, stop.
whoami=`oc whoami`
if [[ "$whoami" != "system:admin" ]]; then
  echo "==================================
Script failed user validation!
=================================="
  exit 1
fi

#Check for the masters
#TODO improve this as it might pickup a node thats marked as unscheduled
masters_array=`oc get nodes | grep "SchedulingDisabled" | awk '{print $1}'`
#echo "masters list: $masters_array"
#Check to see that we got a response, if not just die.
if [ -z "$masters_array" ]; then

  echo "=====================================================================
No masters found!  This should not happen, so something bad occured.
====================================================================="
  exit 1

fi

#Process the list of masters, and create a comma seperated string
readarray -t masters <<<"$masters_array"
for master in "${masters[@]}"
do
  masters_list+="https://${master}:2379,"
done
#Remove trailing comma.
masters_list=`echo ${masters_list%?}`

#Stop all the etcd services on each master
for master in "${masters[@]}"
do
  stop_etcd $master
done

#Just make sure all etcd are stopped.
echo "Waiting 30 seconds to make sure etcd is stopped."
sleep 30

#Backup etcd, currenly only the etcd on the current master node will be backed up
#According to the docs only a single etcd needs to be saved
#https://docs.openshift.com/container-platform/3.3/admin_guide/backup_restore.html#cluster-backup
backup_master_etcd

#Start all the etcd services on each master
for master in "${masters[@]}"
do
  start_etcd $master
done

#Just make sure all etcd are started.
echo "Waiting 30 seconds to make sure etcd is started."
sleep 30

#Query etcd to get the status of the cluster
etc_health_string=`etcdctl --endpoints ${masters_list} \
--ca-file=/etc/origin/master/master.etcd-ca.crt \
--cert-file=/etc/origin/master/master.etcd-client.crt \
--key-file=/etc/origin/master/master.etcd-client.key \
cluster-health`

#Grep out the status
status=`echo $etc_health_string | grep "cluster is healthy"`

#If the var is null, then the cluster is not healthy
if [ -z "$status" ]; then

  echo "etcd cluster is not health"
  exit 1

else

  echo "etcd cluster is healthy, great success."

fi
