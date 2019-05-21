# Capacity Planning and Resource Utilisation Grafana Dashboards


Resource Quota management is necessary to properly utilize resources across OpenShift cluster. This can be achieved by two ways:
1. Creating Resource Quota per Project
2. Creating Cluster Resource Quota

However, using both types of quota management at the same time will not provide proper resource accountinng and management.

## Resource Quota

**Assumption:** Openshift cluster has following labels in place:
* Nodes are labeld, for example:
  * label_node_role_kubernetes_io_compute="true"
  * label_node_role_kubernetes_io_compute_special="true"
* Projects are annotated with a Node Selector, for example:
  * annotation_openshift_io_node_selector="node-role.kubernetes.io/compute-special=true"
  * annotation_openshift_io_node_selector="node-role.kubernetes.io/compute-special=true"
* Projects are configured with Reource Quota, for example:
```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: core-object-counts
spec:
  hard:
    requests.cpu: "1800m"
    requests.memory: "1024Mi"
    glusterfs.storageclass.storage.k8s.io/requests.storage: "10Gi"
  scopes:
  - NotTerminating
```
* All Pods are using cpu and memory requests and limits.


**Implementation:** 
Import the "Capacity Planning (ResourceQuota).json" Dashboard in [custom grafana](https://github.com/redhat-cop/openshift-toolkit/tree/master/custom-dashboards). Necessary labels are required to work the dashboard. If the cluster has different types of labels, please change the variables from dashboard settings.


## Cluster Resource Quota

**Assumptions:**
Openshift cluster has following labels in place:
* Nodes are labeld. This is additional labels from default node role labels, for example:
  * zone=dev
  * zone=qa
* Projects are also labeld, for example:
  * zone=dev
  * zone=qa
* In addition to the above Project Label, ClusterResourceQuota object will use a Project Selector label. So, lable the project in accordance with the Cluster Resource Quota that the project will be tied to:
  * lob=lob1
  * lob=lob2
* Also a node-selector for the project

A typical project will be provisioned as:
```
oc patch namespace test-quota-1 -p '{"metadata": {"labels": {"lob": "lob1"}}}'
oc patch namespace test-quota-1 -p '{"metadata": {"labels": {"zone": "dev"}}}'
oc patch namespace test-quota-1 -p '{"metadata": {"labels": {"router": "dev"}}}'
oc patch namespace test-quota-1 -p '{"metadata": {"annotations": {"openshift.io/node-selector": "node-role.kubernetes.io/compute=true"}}}'
```
##### (One additional label is shown here to utilize router sharding)

* ClusterResourceQuota Object is created:
```
apiVersion: quota.openshift.io/v1
kind: ClusterResourceQuota
metadata:
  name: lob1-dev
  labels:
    zone: dev
spec:
  quota:
    hard:
      glusterfs.storageclass.storage.k8s.io/requests.storage: 10Gi
      requests.cpu: "1"
      requests.memory: 1Gi
  selector:
    labels:
      matchLabels:
        lob: lob1
        zone: dev
  scopes:
  - NotTerminating
  ```

**Implementation:** 
Import the "Capacity Planning (ClusterResourceQuota).json" Dashboard in [custom grafana](https://github.com/redhat-cop/openshift-toolkit/tree/master/custom-dashboards). Necessary labels are required to work the dashboard. If the cluster has different types of labels, please change the variables from dashboard settings.