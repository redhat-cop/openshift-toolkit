# grafana-custom
Custom Grafana for OpenShift 3.11

By default OpenShift 3.11 Grafana is a read-only instance. Many organizations may want to add new custom dashboards. This custom grafana will interact with existing Prometheus and will also add all out-of-the-box dashboards plus few more interesting dashboards which may require from day to day operation. Custom Grafana pod uses OpenShift oAuth to authenticate users and assigns "Admin" role to all users so that users can create their own dashboards for additional monittoring.

* Clone the repository and switch into the directory. Log in as a cluster-admin user and switch to openshift-monitroing project:
```
cd grafana-custom
oc project openshift-monitoring
```

* Create a Service Account named grafana-custom:
```
oc create -f grafana-sa.yml
```

* Assign existing "grafana" role to grafana-custom Service Account:
```
oc create -f grafana-clusterrolebinding.yml
```

* Create a secret for grafana-custom configuration:
```
oc create -f grafana-custom-config-secret.yml
```

* Create few custom dashboards. All existing OpenShift dashboards will be imported automatically:
```
oc create -f dashboard-capacity.yml
oc create -f dashboard-master-api.yml
oc create -f dashboard-pods.yml
oc create -f dashboard-traffic.yml
```

* Create a service for grafana-custom:
```
oc create -f grafana-service.yml
```

* Create a route for the grafana-custom:
```
oc create -f grafana-route.yml
```

* Finally, create the grafana-custom Pod:
```
grafana-deployment.yml
```
