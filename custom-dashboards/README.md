# Getting Started with Custom Dashboarding on OpenShift using Grafana

This repository contains scaffolding and automation for developing a custom dashboarding strategy on OpenShift using the OpenShift Monitoring stack. This includes the following components:

* **Playbook to Deploy OpenShift Monitoring Stack**

  For clusters that do not already have the monitoring stack installed, the `monitoring.yml` playbook is provided to deploy it. This playbook has been shown to work (though is not supported by Red Hat) as far back as OpenShift 3.9.
* **Custom Grafana for OpenShift 3.11**

  By default OpenShift 3.11 Grafana is a read-only instance. Many organizations may want to add new custom dashboards. This custom grafana will interact with existing Prometheus and will also add all out-of-the-box dashboards plus few more interesting dashboards which may require from day to day operation. Custom Grafana pod uses OpenShift oAuth to authenticate users and assigns "Admin" role to all users so that users can create their own dashboards for additional monitoring.
* **Starter Dashboards**

  Several dashboards are available to be provisioned in your Grafana instance as a starting point for Dashboard Development. See the [dashboards](.openshift/dashboards/) directory for more info.

## Deploying the Entire Project

An [OpenShift Applier](https://github.com/redhat-cop/openshift-applier) inventory has been supplied for deployment convenience. Two playbooks are also provided. The first is to deploy the OpenShift Monitoring stack, using [openshift-ansible](https://github.com/openshift/openshift-ansible), the second deploys the custom Grafana.

1. First, you must download the prerequsite repositories, [OpenShift Ansible](https://github.com/openshift/openshift-ansible), and [OpenShift Applier](https://github.com/redhat-cop/openshift-applier).

        ansible-galaxy install -r requirements.yml -p galaxy


2. (Optional) If you are running on an OpenShift Cluster older than 3.11, or your cluster did not have the monitoring stack installed at first install, you can use the following command to install the monitoring stack:

        ansible-playbook -i /path/to/cluster/inventory/ monitoring.yml

3. Finally, run the apply.yml playbook to deploy Grafana and all of the Dashboards.

        ansible-playbook -i .applier/ apply.yml

## Selectively Deploying Dashboards

The above automation deploys everything in this project. If you would like to deploy only specific dashboards of your choosing, you can do so by specifying which applier tags to provision.

The following command is equivalent to the above:

    ansible-playbook -i .applier/ apply.yml -e include_tags=infrastructure,dashbard-cluster-status,dashboard-capacity,dashboard-sdm
