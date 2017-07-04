# OpenShift Admin Bash Scripts

This folder contains a collection of scripts to clean an OpenShift cluster.

These scripts can be run natively on the superior Linux OS, or MacOS.  Windows requires using a bash emulator (GitBash).

## Script Overview

The following table outlines the scripts and purpose.

Script Name | Description | Notes
--- | --- | ---
`cleanup-builds.sh` | Deletes builds older than 30 days. | Parameters required, check script doc.
`delete-dead-pods.sh` | Deletes all the dead or completed pods on the cluster. | Parameters and auth required, check script doc.
`delete-expired-replication-controllers.sh` | Deletes all RC's older than 60 days. | Parameters and auth required, check script doc.
