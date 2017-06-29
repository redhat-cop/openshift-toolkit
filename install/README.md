# Sample Inventory Structure for an HA OpenShift Cluster

This directory represents a sample Infrastructure as Code repo used to manage one or more OpenShift clusters. This is meant to be supporting material for [Installing an HA OpenShift Cluster](http://playbooks-rhtconsulting.rhcloud.com/playbooks/installation/).

This directory contains several different versions of inventories for a fictional OpenShift cluster, `c1-ocp.myorg.com`. The different directories here depict several iterations one might go through while standing up an OpenShift cluster. Those phases are as follows:

* [Base Install](./c1-ocp.myorg.com-base): This configuration represents a bare bones install of a Highly Available, disconnected cluster.
* [LDAP Authentication](./c1-ocp.myorg.com-ldap): This configuration shows how LDAP Authentication can be layered on the base install.
* [Metrics] (Coming Soon)
* [Loggin] (Coming Soon)
* [Custom Named Certificates] (Coming Soon)

## Usage

Any of the inventories should be fairly runnable out of the box, assume you've got infrastructure to match. Use it as a base to start your own cluster builds, or build your infrastructure using the [Install Guide](http://playbooks-rhtconsulting.rhcloud.com/playbooks/installation/) and run it directly:

```
ansible-playbook -i ./c1-ocp.myorg.com-base/hosts /usr/share/ansible/openshift-ansible/playbooks/byo/config.yml
```
