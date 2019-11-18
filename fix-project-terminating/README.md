# Fix project terminating 

In some cases, projects/namespaces get stuck in a `terminating` state. In most cases this is due to one or more finalizers on objects within the projects  - including for Custom Resources (CRs) based on Custom Resource Definitions (CRDs). For these, the following `patch` command can be used to remove the finalizer and hence recover from the terminating state.

### Patch Command to remove finalizer from an object (non-project/namespace)

```bash
> oc patch <object-type> <object-name> -p '{"metadata":{"finalizers": []}}' --type=merge
```

### Patch project/namespace using curl

In other cases, however, the project/namespace seems stuck by having a finalizer on the project itself. In that case, the script found here - `fix-terminating.sh` can be utilized to patch the namespace utilizing curl. Note that this script needs to be executed where the necessary certs exists (obtained on the OpenShift master node). 

```bash
> bash fix-terminating.sh <cluster-url> <namespace>
```
