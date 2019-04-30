# grafana-custom
Custom Grafana for OpenShift 3.11

By default OpenShift 3.11 Grafana is a read-only instance. Many organizations may want to add new custom dashboards. This custom grafana will interact with existing Prometheus and will also add all out-of-the-box dashboards plus few more interesting dashboards which may require from day to day operation. Custom Grafana pod uses OpenShift oAuth to authenticate users and assigns "Admin" role to all users so that users can create their own dashboards for additional monitoring.

**To deploy it manually under openshift-monitoring project alongside existing Grafana**
* Clone the repository and switch into the directory. Log in as a cluster-admin user and switch to openshift-monitroing project:
```
cd grafana-custom
oc project openshift-monitoring
```

* Create a Service Account named grafana-custom:
```
oc apply -f grafana-sa.yml
```

* Assign existing "grafana" role to grafana-custom Service Account:
```
oc apply -f grafana-clusterrolebinding.yml
```

* Create a secret for grafana-custom configuration:
```
oc apply -f grafana-custom-config-secret.yml
```

* Create few custom dashboards. All existing OpenShift dashboards will be imported automatically:
```
oc apply -f dashboard-capacity.yml
oc apply -f dashboard-master-api.yml
oc apply -f dashboard-pods.yml
oc apply -f dashboard-traffic.yml
```

* Create a service for grafana-custom:
```
oc apply -f grafana-service.yml
```

* Create a route for the grafana-custom:
```
oc apply -f grafana-route.yml
```

* Finally, create the grafana-custom Pod:
```
oc apply -f grafana-deployment.yml
```

**To deploy it using openshift-applier:**

* Copy all the files under inventory_dir/files/grafana-custom

* Add below variables in group_vars/all.yaml (or in appropriate inventory file)
```
openshift_cluster_content:
- object: openshift-monitoring-grafana-custom
  content:
  - name: Create SA grafana-custom
    file: "{{ inventory_dir }}/files/grafana-custom/grafana-sa.yml"
    namespace: openshift-monitoring
  - name: Assign grafana role to SA grafana-custom
    file: "{{ inventory_dir }}/files/grafana-custom/grafana-clusterrolebinding.yml"
    namespace: openshift-monitoring
  - name: Create grafana-custom-config Secret
    file: "{{ inventory_dir }}/files/grafana-custom/grafana-custom-config-secret.yml"
    namespace: openshift-monitoring
  - name: Create dashboard-capacity ConfgiMap
    file: "{{ inventory_dir }}/files/grafana-custom/dashboard-capacity.yml"
    namespace: openshift-monitoring
  - name: Create dashboard-master-api ConfgiMap
    file: "{{ inventory_dir }}/files/grafana-custom/dashboard-master-api.yml"
    namespace: openshift-monitoring
  - name: Create dashboard-pods ConfgiMap
    file: "{{ inventory_dir }}/files/grafana-custom/dashboard-pods.yml"
    namespace: openshift-monitoring
  - name: Create dashboard-traffic ConfgiMap
    file: "{{ inventory_dir }}/files/grafana-custom/dashboard-traffic.yml"
    namespace: openshift-monitoring
  - name: Create grafana-custom Service
    file: "{{ inventory_dir }}/files/grafana-custom/grafana-service.yml"
    namespace: openshift-monitoring
  - name: Create grafana-custom Route
    file: "{{ inventory_dir }}/files/grafana-custom/grafana-route.yml"
    namespace: openshift-monitoring
  - name: Deploy grafana-custom Pod
    file: "{{ inventory_dir }}/files/grafana-custom/grafana-deployment.yml"
    namespace: openshift-monitoring
```
