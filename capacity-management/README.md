## Cluster Capacity Report (cluster_capacity.py)

The `capacity/cluster_capacity.py` script generates a report showing how full a kubernetes cluster is. It can be run from anywhere there is an active `~/.kube/config` context and requires at least `cluster-reader` or equivalent permissions.

The script can be run with no arguments, but must be run with Python 3.

```
pip install -r requirements.txt
oc login ...
./cluster_capacity.py
```

The script will total the allocatable CPU and Memory from all nodes (via `status.allocatable`), and the total of all configured `resources.requests` and `resources.limits` from pods in the cluster, and calculated to total allocated resources. The report generated looks like the following:

```
Total Cluster Size:
----
	Memory:	151.23707342147827 Gi
	CPU:	37.2 Cores

Amount Claimed By Quota:
----
	Memory:	0.0 Gi (0.0%)
	CPU:	0 Cores (0.0%)

Total Limits:
----
	Memory:	107.326858619228 Gi (70.96597163059474%)
	CPU:	10.894999999999996 Cores (29.287634408602138%)

Total Requests:
----
	Memory:	41.29272060096264 Gi (27.30330577469265%)
	CPU:	9.074999999999985 Cores (24.39516129032254%)

```
