## Cluster Management

This directory contains scripts specific to cluster managment intended to be run after an OCP installation for operationalization purposes.

### Contents:

1. Garbage collection
- Sets up spotify docker-gc on hosts. Should be run a standard 'bring your own' OpenShift-ansible inventory file. The playbook will set up garbage collection on all host with the [node] designation. 
- View the documentation for spotify docker-gc here: [LINK](https://github.com/spotify/docker-gc)
