# OpenShift Custom Autoscaler Quickstart

The following illustrates how one might use OpenShift's [metrics stack](https://docs.openshift.com/container-platform/latest/install_config/cluster_metrics.html) (Hawkular, Cassandra, Heapster) to develop customized application autoscaling.

## Running & Testing

This script makes a few assumptions about your application

* The pods are managed by a `deploymentConfig`
* The `deploymentConfig` is named the same as the app. (in this case, `myapp`)
* The `deploymentConfig` has memory limits set on the containers. i.e.
  ```
  apiVersion: v1
  kind: DeploymentConfig
  metadata:
    name: myapp
  spec:
    template:
      spec:
        container:
        - resources:
            limits:
              memory: 140Mi

  ```

Before running the script, you need to export a few variables into your environment. The following represents a minimal setup. A full description of all variables is below.

```
export NAMESPACE=myproject
export TOKEN=`oc whoami -t`
export APP_NAME=myapp
export HAWKULAR_HOSTNAME=hawkular-metrics.apps.ocp-c1.myorg.com
```

From there we can simply run our script.

```
./scale.py
```

The script will continue to run until exited, either through Ctrl+C or killing the pid.

## Environment Variables

| Variable Name | Default Value | Description |
| --------------| ------------- | ----------- |
| `NAMESPACE` | n/a; Required | Namespace the app is running in. |
| `TOKEN` | n/a; Required | OpenShift User or ServiceAccount token. Can be retrieved using `oc whoami -t` for users or `oc serviceaccount get-token <sa name>` for serviceaccounts. |
| `APP_NAME` | n/a; Required | Name of DeploymentConfig. Must match name shown in `oc get dc` |
| `HAWKULAR_HOSTNAME` | n/a; Required | Route hostname for hawkular service. i.e. `oc get route hawkular-metrics -n openshift-infra` |
| `METRIC_PULL_INTERVAL_SECONDS` | 60 | Number of seconds between each scale up check |
| `SCALE_UP_THRESHOLD` | .7 | Floating numeric value 0-1; Percentage of total memory used over which a scale-up will happen |
| `CA_CERT` | False | Path to a CA Certificate file to validate Hawkular certificate. Default value of `False` will turn off certificate checks and flash a warning message. |



## Issues, Limitations & Future Enhancements

- Solution should be deployed as a pod in openshift.
- Currently only scales up, not down
- Implementation very specific to memory, but could probably be genericized to pull some other metric.
- Needs better error handling
