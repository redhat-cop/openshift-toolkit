# Capacity Planner App

Capacity Planner is an application that helps cluster administrators get a sense for how utilized their clusters are by several different measures.

## Usage

There are several ways to consume Capacity Planner.

### CLI Mode

Capacity Planner has a cli script that can be used to quickly get data about a cluster to which you are logged in. It can be run with no arguments for the default behavior

```
pip3 install -r requirements.txt
oc login ...
./cli.py
```

The script will total the allocatable CPU and Memory from all nodes (via `status.allocatable`), and the total of all configured `resources.requests` and `resources.limits` from pods in the cluster, and calculated to total allocated resources. By default, the output will be a generated report that looks like the following:

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

If you'd like to get more detail, that includes info about individual nodes, namespaces, and pods, you can print the raw json data to the console.

```
$ cly.py -o json
$ ./cli.py -o json
{
  "cluster": {
    "allocatable": {
      "cpu": 37.2,
      "memory": 162389571072
    },
    "quota": {
      "cpu": 6,
      "memory": 30064771072
    },
    "requests": {
      "cpu": 10.704999999999988,
      "memory": 52260761392
    },
    "limits": {
      "cpu": 11.444999999999997,
      "memory": 120870092906
    }
  },
  "nodes": {
    "app-node-0.example.com": {
      "cpu": 5.6,
      "memory": 24406280704
    },
		...
	},
	"namespaces" : {
		...
	}
}
```

### Web Application Mode

Capacity Planner can also be run as a web app on OpenShift, which serves the json content above. Run the following commands to deploy:

```
oc new-project capacity-planner
oc apply -f rbac.yaml
oc apply -f capacity-planner.yaml
```

Once deployed, the API will be exposed through a Route at something like http://api-capacity-planner.apps.example.com

#### Running Locally

For development purposes, the web app can be run locally by executing the `app.py` program.

```
pip3 install -r requirements.txt
oc login ...
./app.py
```
