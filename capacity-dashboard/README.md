# Capacity Planning and Resource Utilisation Grafana Dashboards


Resource Quota management is necessary to properly utilize resources across OpenShift cluster. This can be achieved by two ways:
1. Creating **Resource Quota** per Project.
2. Creating **Cluster Resource Quota** across OpenShift cluster.

However, using both types of quota management at the same time will not provide proper resource accountinng and management. Follow only one method listed below:

## Resource Quota

**Assumption:** Openshift cluster has following labels in place:
* Nodes are labeld, for example:
  * label_node_role_kubernetes_io_compute="true"
  * label_node_role_kubernetes_io_compute_special="true"
* Projects are annotated with a Node Selector, for example:
  * annotation_openshift_io_node_selector="node-role.kubernetes.io/compute=true"
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
Import the "DashBoard-CapacityPlanning-(ResourceQuota).json" Dashboard in [custom grafana](https://github.com/redhat-cop/openshift-toolkit/tree/master/custom-dashboards). Necessary labels are required to work the dashboard. If the cluster has different types of labels, please change the variables from dashboard settings.


## Cluster Resource Quota

**Assumptions:**
Openshift cluster has following labels in place:
* Nodes are labeld. This is an additional label from default node role/group labels, for example:
  * nodegroup=default
  * nodegroup=special
* Projects are also labeld, for example:
  * nodegroup=default
  * nodegroup=special
* In addition to the above Project Label, ClusterResourceQuota object will use a Project Selector label. So, lable the project in accordance with the Cluster Resource Quota that the project will be tied to:
  * lob=lob1
  * lob=lob2
* Also a node-selector for the project

In summery, a typical project will be provisioned as:
```
oc patch namespace test-quota-1 -p '{"metadata": {"labels": {"lob": "lob1"}}}'
oc patch namespace test-quota-1 -p '{"metadata": {"labels": {"nodegroup": "default"}}}'

oc patch namespace test-quota-1 -p '{"metadata": {"annotations": {"openshift.io/node-selector": "node-role.kubernetes.io/compute=true"}}}'
```


* ClusterResourceQuota Object is created:
```
apiVersion: quota.openshift.io/v1
kind: ClusterResourceQuota
metadata:
  name: lob1-internal
  labels:
    nodegroup: default
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
        nodegroup: default
  scopes:
  - NotTerminating
  ```

* kube-state-metrics does not scrape ClustreResourceQuota as of version 3.11.98. We have to deploy [openshift-state-metrics](https://github.com/shah-zobair/openshift-state-metrics) to address this issue. An RFE has been submitted to enable this feature. 
To deploy openshift-state-metrics:
```oc apply -f openshift-state-metrics/manifests/ -n openshift-monitoring```


**Implementation:** 
Import the "DashBoard-CapacityPlanning-(Custom Resource Quota).json" Dashboard in [custom grafana](https://github.com/redhat-cop/openshift-toolkit/tree/master/custom-dashboards). Necessary labels are required to work the dashboard. If the cluster has different types of labels, please change the variables from dashboard settings.
