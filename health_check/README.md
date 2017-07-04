# OpenShift Admin Bash Scripts

This folder contains a collection of scripts to perform additional health checks on OpenShift logging and metrics.

These scripts can be run natively on the superior Linux OS, or MacOS.  Windows requires using a bash emulator (GitBash).

## Script Overview

The following table outlines the scripts and purpose.

Script Name | Description | Notes
--- | --- | ---
`elasticsearch-health-check-ocp33.sh` | Returns the health of the integrated ES cluster. Only works on OCP =< 3.3  | Parameters and auth required, check script doc.
`elasticsearch-health-check-ocp34.sh` | Returns the health of the integrated ES cluster. Only works on OCP >= 3.4  | Parameters and auth required, check script doc, and will not work on GitBash (Windows).
`metrics-health-check.sh` | Checks if the metrics stack is up and running. | Parameters and auth required, check script doc.
