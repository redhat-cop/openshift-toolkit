# Example

to create an example scenario, label a set of nodes with the label `nodegroup=group1`, then run the following commands:

```shell
oc adm new-project p1q1 --node-selector nodegroup=group1
oc label namespace p1q1 quota=quota1
oc adm new-project p2q1 --node-selector nodegroup=group1
oc label namespace p2q1 quota=quota1
oc adm new-project p1q2 --node-selector nodegroup=group1
oc label namespace p1q2 quota=quota2
oc adm new-project p2q2 --node-selector nodegroup=group1
oc label namespace p2q2 quota=quota2
oc apply -f cluster_quota.yaml
```
