# Fix project terminating 

In some cases, projects/namespaces get stuck in a `terminating` state. In most cases this is due to one or more finalizers on objects within the projects  - including for Custom Resources (CRs) based on Custom Resource Definitions (CRDs). For these, the following `patch` command can be used to remove the finalizer and hence recover from the terminating state.

### Find out what's holding up the termination of the project

```bash
> oc get project <project-name> -o yaml
```

Look in the `status` of the output to see what needs to be patched. In the example below we'll need to patch `cephclusters.ceph.rook.io`

```
...
status:
  conditions:
  - lastTransitionTime: "2020-03-26T10:01:05Z"
    message: 'Some content in the namespace has finalizers remaining: cephcluster.ceph.rook.io
      in 1 resource instances'
    reason: SomeFinalizersRemain
    status: "True"
    type: NamespaceFinalizersRemaining
```

### Patch Command to remove finalizer from an object (non-project/namespace)

```bash
> oc patch <object-type> <object-name> -p '{"metadata":{"finalizers": []}}' --type=merge
```

### Patch project/namespace script using curl and oc client or certs

In other cases, however, the project/namespace seems stuck by having a finalizer on the project itself. In that case, the script found here - `fix-terminating.sh` can be utilized to patch the namespace utilizing curl. Note that this script may need to be executed where the necessary certs exists (obtained on the OpenShift master node).

with certs

```bash
> bash fix-terminating.sh <cluster-url> <namespace>
```

or without certs and with the oc client

```bash
> bash fix-terminating.sh -c <namespace>
```
