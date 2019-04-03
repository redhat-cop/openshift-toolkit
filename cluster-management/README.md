# Cluster Management

This directory contains scripts specific to cluster managment intended to be run after an OCP installation for operationalization purposes.

## Cluster Capacity Report (cluster_capacity.py)

The `capacity/cluster_capacity.py` script generates a report showing how full a kubernetes cluster is. It can be run from anywhere there is an active `~/.kube/config` context and requires at least `cluster-reader` or equivalent permissions.

The script can be run with no arguments, but must be run with Python 3.

```
pip install -r requirements.txt
oc login ...
capacity/cluster_capacity.py
```

The script will total the allocatable CPU and Memory from all nodes (via `status.allocatable`), and the total of all configured `resources.requests` and `resources.limits` from pods in the cluster, and calculated to total allocated resources. The report generated looks like the following:

```

CPU Requests                   CPU Limits                     Memory Requests                Memory Limits                 
------------                   ----------                     ---------------                -------------                 
8.274999999999984 Cores (22%)  3.6550000000000002 Cores (10%) 54.84904270991683Gi (36%)      57.365921119228005Gi (38%)    

```

## Garbage collection

- Sets up spotify docker-gc on hosts. Should be run a standard 'bring your own' OpenShift-ansible inventory file. The playbook will set up garbage collection on all host with the [node] designation.
- View the documentation for spotify docker-gc here: [LINK](https://github.com/spotify/docker-gc)
