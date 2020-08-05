# OpenShift Admin Bash Scripts

This folder contains a collection of script to backup certain part of an OpenShift cluster.

These scripts can be run natively on the superior Linux OS, or MacOS.  Windows requires using a bash emulator (GitBash).

## Script Overview

The following table outlines the scripts and purpose.

Script / Playbook Name | Description | Notes
--- | --- | ---
`ocp-master-cert-backup.sh` | Creates a backup of the master certificates. | Must be run on an OCP master node.
`ocp-project-backup.sh` | Creates a yaml backup of all projects in the OpenShift cluster. | Must be run on an OCP master node.
`ocp-etcd3-pods-backup.sh` | Creates a backup of the etcd (data snapshot & config). Also manages backup retention. | Must be run on the OCP nodes running the etcd static Pods (usually masters).
`master-backup.yaml` | Ansible clone of the bash `ocp-master-cert-backup.sh` script.
`ocp_backup.yml` | Backup masters and nodes using the Day-2 Guide | Run from a control host
`./roles` | Roles use in the `ocp_backup.yml` playbook
