#!/bin/bash 

set -Exeuo pipefail

# Date: 08/01/2018
#
# Script Purpose: Create a backup of all projects on the OCP cluster.
# Version       : 1.01
#

#===============================================================================
#This script must be executed on cluster master node.
#===============================================================================


for pid in $(pidof -x `basename "$0"`); do
    [ $pid != $$ ] && echo "[$(date)] : `basename "$0"` : Process is already running with PID $pid" && exit 1
done

#Update this path to point to the backup location.
readonly ARCHIVE_LOCATION="/opt/backups/master" && [ ! -d $ARCHIVE_LOCATION ] && mkdir -p $ARCHIVE_LOCATION

# Check if executed as root
if [[ $EUID -ne 0 ]]; then
  echo "ERROR: This script must be run as root. Aborting."
  exit 1
fi

# Check if executed on OSE master
if ! systemctl status `systemctl list-units --plain  -t service | egrep master-api |cut -d. -f1` >/dev/null 2>&1; then
  echo "ERROR: This script must be run on an OpenShift master. Aborting."
  exit 1
fi


#Login to ocp
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

#Get the hostname of the OCP console
ocp_hostname_with_port=`oc version | grep Server | awk -F/ '{print $3}'`
ocp_hostname=`echo ${ocp_hostname_with_port} | awk -F: '{print $1}'`
echo "OCP Cluster: ${ocp_hostname}"

#Set the yaml backup path
temp_backup_path="${ocp_hostname}"

#Check for the project
project_list=`oc projects -q`
#Check to see that we got a response, if not just die.
if [ -z "$project_list" ]; then

  echo "=====================================================================
No projects found!  This should not happen, so something bad occured.
====================================================================="
  exit 1

fi

#Process the list of projects and export them if they are valid
readarray -t projects <<<"$project_list"
for project in "${projects[@]}"
do

  #check to see if the project is actually validation
  project_exists=`oc projects -q | grep ${project}`
  if [ -n "$project_exists" ]; then

    echo "Backing up project: ${project}"

    #Create a variable to hold
    yaml_dir="${temp_backup_path}/${project}"

    #Make the project directory
    mkdir -p ${yaml_dir}

    set +e
    #Export all bc,dc,is,route,svc yamls
    oc export all -n ${project} -o yaml > ${yaml_dir}/project.yaml

    #Export all the rolebindings
    oc get rolebindings -n ${project} -o yaml --export=true > ${yaml_dir}/rolebindings.yaml

    #Export any project serviceaccounts
    oc get serviceaccount -n ${project} -o yaml --export=true > ${yaml_dir}/serviceaccount.yaml

    #Export any project secrets
    oc get secret -n ${project} -o yaml --export=true > ${yaml_dir}/secret.yaml

    #Export any project pvc
    oc get pvc -n ${project} -o yaml --export=true > ${yaml_dir}/pvc.yaml
    set -e
  else

    #Found an invalid project name, somehting bad may have happened, but we'll
    #just continue.
    echo "Project: ${project}, is not a valid project."

  fi

done


#Now tar it.
tar_archive="${ARCHIVE_LOCATION}/${temp_backup_path}-$(date -u '+%Y%m%d-%H%M%S').tar.gz"
echo "Creating archive of project backups at: ${tar_archive}"
tar -czf ${tar_archive}  ${temp_backup_path}

echo "Cleanup yamls..."
rm -rf ${temp_backup_path}

#Yea!
echo "Great Success"
