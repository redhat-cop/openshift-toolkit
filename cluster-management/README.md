## Cluster Management

This directory contains scripts specific to cluster managment intended to be run after an OCP installation for operationalization purposes.

### Contents:

1. Garbage collection
- Sets up spotify docker-gc on hosts. Should be run a standard 'bring your own' OpenShift-ansible inventory file. The playbook will set up garbage collection on all host with the [node] designation. 
- View the documentation for spotify docker-gc here: [LINK](https://github.com/spotify/docker-gc)

2. Resource Management
- cluster_resource_report uses python-requests to talk to the openshift api. It attempts to determine on a per-host basis what resource requests and limits are active on a given host
- the script assumes it is being run on a master as root so that it can extract the /root/.kube/config file
