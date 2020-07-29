# OCP-Prep Playbook
## Author: Bill Strauss 

OCP-prep was created as a supporting repo to the deployment of OpenShift 3.X, and to house playbooks and roles to be ran prior to an OpenShift 3.X deployment.  Its purpose is to automate deployment-preparation tasks, as well as assisting with the streamlining of the OpenShift deployment process.  Its core focus is to prepare for an OpenShift 3.X deployment (specifically version 3.11) in a disconnected environment, utilizing a Gluster storage backend, but has some functionality to support other OCP (OpenShift Container Platform) architectures as well. 

## OCP-Prep Tasks

This repo (currently) includes the following automated tasks:

- [SSH Key](playbooks/configure_ssh) generation and dissemination.
- [Satellite](playbooks/configure_satellite) subscription/registration.
- Installation of OpenShift-specific and additional/recommended [Packages](playbooks/package_install).
- Preparing for an OCP deployment in a [FIPS](playbooks/FIPS_env_preparation) enabled environment. This includes changes to both the bastion/ansible host as well as the nodes within the OCP cluster.
- Configuration of [OCP storage](playbooks/configure_ocp_storage), including wiping specified drives, creating/mounting filesystems, etc..
- Configuration of [Docker storage](playbooks/configure_docker_storage).
- Configuration of [rsyslog](playbooks/configure_rsyslog) for OCP advanced auditing.
- Initial configuration of [htpasswd](playbooks/configure_htpasswd), including generating username/password hash and incorporating these values into the inventory file, in preparation for using htpasswd authentication as part of the OCP deployment.

## Inventory Options

**Note:** Most of the important variables are included in "inventories/"your env"/group_vars/all.yml" and will be described, in detail, in their respective sections below. Locations of additional variables (if any), are also addressed/highlighted in their respective sections below.

**Note:** Within the file mentioned above, each task has a True/False Boolean to indicate which task(s) to perform. If not specified, they all default to "False", meaning they will not be included/ran when the playbook is implemented unless otherwise specified as an "-e" variable entered at the time the command is ran.

## Playbook execution

If password authentication is NOT required to access the nodes:

```bash
> ansible-playbook -i <inventory file> playbooks/OpenShift_deploy_prep.yml
```

If password authentication IS required to access any OCP nodes AND the "ssh keygen" playbook has yet to be run:

```bash
> ansible-playbook -i <inventory file> playbooks/OpenShift_deploy_prep.yml --ask-pass
```

## Primary Prerequisites

A complete and properly structured inventory/hosts file must exist. See OCP installation documentation for details on how to build an OCP inventory file.

All nodes in the OCP cluster must be identified in the inventory file, and be included in their respective groups in the inventory file.

All nodes in the OCP cluster must be online and accessible.

SSH handshake must be accepted, and their respective host keys added to .ssh/known_hosts file on the bastion/ansible host, for each node specified in the inventory file.

If OCP Advanced Auditing is to be deployed, the location of the adv-audit.yaml file must be specified in your inventory file (a default/example adv-audit.yaml file is provided at (./files/adv-audit.yaml). Proper structure for the auditing portion of your inventory file can be found in the [Advanced Auditing](https://docs.OpenShift.com/container-platform/3.11/install_config/master_node_configuration.html#master-node-config-advanced-audit) portion of the Red Hat OpenShift documentation.

# SSH Keygen Playbook

This playbook calls/runs the roles and tasks necessary to generate the ssh keys for the bastion/ansible host (if it doesn't exist) and disseminate the pubkey to all hosts in the OCP cluster.

## Prerequisites

Same as the primary prerequisites.

## Roles/Tasks

main role

This role calls the main task

main task

This task calls the individual tasks listed below

ssh\_dir\_create task

This task will create the /home/current_user/.ssh directory if it doesn't exist

ssh\_keygen task

This task will generate the ssh key for the current user on localhost

distribute\_ssh\_pubkey task

This task will copy the newly created (or preexisting) ssh pubkey to the .ssh directory on the remote hosts.

## Group_Vars/all.yml variables

| Name | Description | Default|
|---|---|---|
|copy\_ssh\_keys|Run this play|false|
|ansible\_ssh\_user|User that will ssh to remote hosts||
|ssh\_key\_size|Byte length of ssh key||

## Additional variables

The user's .ssh directory location is specified in the "vars/main.yml" file for this role; however, this shouldn't ever need to be changed.

## Playbook execution

If password authentication is NOT required to access the nodes:

```bash
> ansible-playbook -i <inventory file> playbooks/configure_ssh/main.yml
```

If password authentication IS required to access any OCP nodes AND the "ssh keygen" playbook has yet to be run:

```bash
> ansible-playbook -i <inventory file> playbooks/configure_ssh/main.yml --ask-pass
```

# Satellite Subscription/Registration Playbook
This playbook calls/runs the roles and tasks necessary to register all of the OpenShift nodes with a satellite server.  It also cleans the repos and performs an update on each node.

## Prerequisites

Same as the primary prerequisites.

If registering with RH Subscription Manager or a Satellite server that requires credentials, you will need to include them using the username/password variables specified below.

## Roles/Tasks

main role

This role calls the main task

main task

This task will obtain the necessary satellite packages when a hostname is defined. It then unregisters from the default satellite and then is registered to the new satellite. Lastly, it performs an update on the nodes and cleans temp files created during the task. 

## Group_Vars/all.yml variables

| Name | Description | Default|
|---|---|---|
|rhsm\_register|Run this play|false|
|rhsm\_server\_hostname|Satellite server hostname||
|disable\_pkg\_authenticity\_verification|Dictates if gpgcheck should be disabled|no|
|rhsm\_org\_id|The org id||
|rhsm\_activation\_key|The activation key||

## Additional variables

Within the roles/configure_satellite/tasks/main.yml file, a number of additional optional variables are available for further customization. These include:

| Name | Description | Default|
|---|---|---|
|rhsm\_username|Username|omit|
|rhsm\_password|Password|omit|
|rhsm\_pool\_ids|Pool IDs|omit|
|rhsm\_pool|Pool(s)|omit|

Within the roles/configure_satellite/vars/main.yml file, the location to store the temporary file created during this task, is specified. This is named "satellite\_server\_rpm\_tmp\_dir" and is originally set to "/tmp/".

## Playbook execution

If password authentication is NOT required to access the nodes:

```bash
> ansible-playbook -i <inventory file> playbooks/configure_satellite/main.yml
```

If password authentication IS required to access any OCP nodes AND the "ssh keygen" playbook has yet to be run:

```bash
> ansible-playbook -i <inventory file> playbooks/configure_satellite/main.yml --ask-pass
```

# Package Install Playbook

This playbook calls/runs the roles and tasks necessary to install various common, required and useful packages on the OCP cluster hosts as well as localhost.

## Prerequisites

Same as the primary prerequisites.

## Roles/Tasks

main role

This role calls the main task

main task

This task calls the individual tasks listed below

package_install task

This task installs the necessary packages on localhost and the OCP cluster hosts.

yum_update task

This task updates localhost and the OCP cluster hosts.

## Group_Vars/all.yml variables

| Name | Description | Default|
|---|---|---|
|package_install|Run this play|false|

## Additional variables

Within the roles/package_install/vars/main.yml file, you'll also find the following two variables:

| Name | Description | Default|
|---|---|---|
|localhost\_prep\_pkg\_list|List of packages to be installed on the localhost||
|nodes\_prep\_pkg\_list|List of packages to be installed on the OCP cluster hosts||

The remaining variable in that file can be ignored as it shouldn't be changed.

## Playbook execution

If password authentication is NOT required to access the nodes:

```bash
> ansible-playbook -i <inventory file> playbooks/package_install/main.yml
```

If password authentication IS required to access any OCP nodes AND the "ssh keygen" playbook has yet to be run:

```bash
> ansible-playbook -i <inventory file> playbooks/package_install/main.yml --ask-pass
```

# FIPS Environment Preparation Playbook

This playbook calls/runs the roles and tasks necessary to prepare the environment for an OpenShift/Gluster deployment in a "FIPS enabled" environment.

## Prerequisites

Same as the primary prerequisites.

Should only need to be ran in an environment with FIPS enabled.

## Roles/Tasks

main role

This role calls the main task

main task

This task will apply a number of fixes on each host in the OCP cluster, to address issues that may arise in a "FIPS enabled environment. These tasks include:
- Disabling and stopping the "named" service if present
- Addressing a missing SELinux Policy
- Enabling IPv4 IP Forwarding

It then calls the following task

update\_local\_install\_files task

This task will apply a number of "FIPS-related" fixes on the localhost, including:
- Replacing references to older encryption algorithms within certain config files referenced/utilized during an OCP deployment
- Disabling CHAPS authentication within the block storage class template file

## Group_Vars/all.yml variables

|update\_ocp\_for\_fips\_env|Run this play|false|

## Additional variables

## Playbook execution

If password authentication is NOT required to access the nodes:

```bash
> ansible-playbook -i <inventory file> playbooks/FIPS_env_preparation/main.yml
```

If password authentication IS required to access any OCP nodes AND the "ssh keygen" playbook has yet to be run:

```bash
> ansible-playbook -i <inventory file> playbooks/FIPS_env_preparation/main.yml --ask-pass
```

# OCP Storage Preparation Playbook

This playbook calls/runs the roles and tasks necessary to prepare the storage partitions for an OCP deployment with Gluster storage.

## Prerequisites

Same as the primary prerequisites.

## Roles/Tasks

main role

This role first prompts the user (twice) requesting that they confirm they want to wipe the storage partitions specified in the variables below, in preparation for an OCP deployment.

If the user indicates they would like to proceed with the storage partition wipe, the following task is called

wipe_storage task

This task will wipe all of the partitions indicated in the "docker\_storage\_disk" (on all OCP hosts) and the "gluster\_storage\_disks" (only on hosts in storage group) variables.

Regardless of the answers to the prompts discussed above, the main role then calls the main task.

main task

This task will perform the following, with different variations depending on whether or not the host is included in the "etcd" group:
- Create "sysvg" volume group (if it doesn't exist)
- Create etcd/origin logical volumes
- Create etcd/origin filesystems
- Create etcd/origin mountpoints
- Mount etcd/origin filesystems
- Update "container\_file\_t" SELinux policy

## Group_Vars/all.yml variables

| Name | Description | Default|
|---|---|---|
|configure\_ocp\_storage|Run this play|false|
|sysvg_pv|Physical volume on which to create the sysvg volume group and the logical volumes/filesystems created therein||
|docker\_storage\_disk|Disk that will be used for docker storage on all nodes (typically "/dev/sdb" though this may be different in your environment)||
|gluster\_storage\_disks|Disk that will be used for Gluster storage on storage nodes||
|etcd\_lv\_size|Size of ETCD logical volume created on all "etcd" nodes||
|node\_origin\_lv\_size|Size of ORIGIN logical volume created on all nodes EXCEPT etcd nodes||
|etcd\_origin\_lv\_size|Size of ORIGIN logical volume created on all ETCD nodes||

## Additional variables


## Playbook execution

```bash
> ansible-playbook -i <inventory file> playbooks/configure_ocp_storage/main.yml
```

If password authentication IS required to access any OCP nodes AND the "ssh keygen" playbook has yet to be run:

```bash
> ansible-playbook -i <inventory file> playbooks/configure_ocp_storage/main.yml --ask-pass
```

# Docker Storage Preparation Playbook

This playbook calls/runs the roles and tasks necessary to configure and install docker storage.

## Prerequisites

Same as the primary prerequisites.

## Roles/Tasks

main role

This role calls the main task

main task

This task first calls and runs the below task "docker_install". Afterwards, it configures the "/etc/sysconfig/docker-storage-setup" file, and then proceeds to setup docker storage. Finally, it enables and restarts the docker service.

docker_install task

This task installs the version of docker specified in the "docker\_version" variable discussed below. If no version is specified, it will install the latest version of docker.

## Group_Vars/all.yml variables

| Name | Description | Default|
|---|---|---|
|configure\_docker\_storage|Run this play|false|

## Additional variables

Within the roles/package_install/vars/main.yml file, there is an additional variable "docker\_version", specifying the version of docker to install. As this is item is specific to the version of OCP being deployed, care should be taken to ensure that the version specified in this variable is compatible with the version (major & minor) of OCP being deployed.

## Playbook execution

```bash
> ansible-playbook -i <inventory file> playbooks/configure_docker_storage/main.yml
```

If password authentication IS required to access any OCP nodes AND the "ssh keygen" playbook has yet to be run:

```bash
> ansible-playbook -i <inventory file> playbooks/configure_docker_storage/main.yml --ask-pass
```

# rsyslog Configuration Playbook

This playbook will first ensure that all additional rsyslog config files are included via the rsyslog.conf file on each of the master hosts.  It then ensures the rsyslog.d directory exists. Lastly, it then generates an rsyslog additional config file from template which is meant to account for OCP audit log configuration. This file is then distributed to the hosts "rsyslog.d/" directory in the "masters" group in the OCP inventory file.

## Prerequisites

Same as the primary prerequisites.

## Roles/Tasks

main role

This role calls the main task.

main task

This task performs all of the items mentioned above.

## Group_Vars/all.yml variables

| Name | Description | Default|
|---|---|---|
|configure_rsyslog|Run this play|false|

## Additional variables

All of the variables used to populate the ocp-audit.conf rsyslog config file are specified in defaults/main.yml. These can be changed if necessary, but the variables and their defaults are as follows:

| Name | Default|
|---|---|
|rsyslog\_ocp\_audit\_log\_input\_file\_name|/var/log/origin/audit-ocp.log|
|rsyslog\_ocp\_audit\_log\_input\_file\_tag|audit_ocp|
|rsyslog\_ocp\_audit\_log\_input\_file\_state\_file|audit-log|
|rsyslog\_ocp\_audit\_log\_input\_file\_facility|local6|

## Playbook execution

If password authentication is NOT required to access the nodes:

```bash
> ansible-playbook -i <inventory file> playbooks/configure_rsyslog/main.yml
```

If password authentication IS required to access any OCP nodes AND the "ssh keygen" playbook has yet to be run:

```bash
> ansible-playbook -i <inventory file> playbooks/configure_rsyslog/main.yml --ask-pass
```

# htpasswd Initial Configuration Playbook

This playbook calls/runs the roles and tasks which first prompts the user to enter username(s) (comma delimited), subsequently prompting the user to enter passwords for each of the previously entered usernames), to be configured as authenticated users for OpenShift. After the user enters the user(s) and passwords, this script will generate the password hashes, and both generate the htpasswd file, and create and insert the "OpenShift\_master\_htpasswd\_file" variable into the specified inventory file, pointing to the htpasswd file that was just generated. If any changes are made to the rsyslog config throughout this play, a handler is notified to restart rsyslog after the play has completed.

## Prerequisites

Same as the primary prerequisites.

## Roles/Tasks

main role

This role calls the main task.

main task

This task creates the empty htpasswd file in a temporary location.  Then, using the username(s)/passwords provided by the user, it generates the password hash(es) and populates the temporary htpasswd file with this data.  Lastly, it will enter the "OpenShift\_master\_htpasswd\_file" variable into the specified inventory file, pointing it to this temporary htpasswd file, to be referenced during the OCP deployment.

## Group_Vars/all.yml variables

| Name | Description | Default|
|---|---|---|
|configure\_htpasswd|Run this play|false|
|ocp\_inventory\_file|Full path of the OCP inventory file||

## Additional variables

The variable for the temporary location of the htpasswd file that will be created on the localhost is specified in the vars/main.yml file as "htpasswd\_file", defaults to "/tmp/htpasswd" and generally shouldn't need to be changed.

## Playbook execution

If password authentication is NOT required to access the nodes:

```bash
> ansible-playbook -i <inventory file> playbooks/configure_htpasswd/main.yml
```

If password authentication IS required to access any OCP nodes AND the "ssh keygen" playbook has yet to be run:

```bash
> ansible-playbook -i <inventory file> playbooks/configure_htpasswd/main.yml --ask-pass
```

## Complete Production Installation Documentation:

- [OpenShift Container Platform](https://docs.OpenShift.com/container-platform/3.11/install/index.html)
- [OKD](https://docs.okd.io/3.11/install/index.html) (formerly OpenShift Origin)
