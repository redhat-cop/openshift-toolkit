# NetworkPolicy

Tools to configure OpenShift with a set of baseline [NetworkPolicy](https://docs.openshift.com/container-platform/latest/admin_guide/managing_networking.html) objects

## Overview

The [OpenShift SDN](https://docs.openshift.com/container-platform/latest/install_config/configuring_sdn.html) offers several plugin implementations. One of these plugins supports NetworkPolicy, which provides for more fine grained policies for communication between pods running on the cluster. Once enabled, all communication between pods within OpenShift are not restricted in any way. The tools within this repository will configure an OpenShift environment with a set of default policies that support a [zero trust network](https://tigera.io/wp-content/uploads/2017/12/wp-tigera-zero-trust-cloud-native-environment.pdf).

The following sections describes the relevant concepts along with tooling to automate the application of these policies to an OpenShift environment. 

## Concepts

### Deny Traffic By Default

Since NetworkPolicy does not restrict pod communication by default, this would violate many of the benefits that are enforced by other SDN plugins (such as the _ovs-multitenant_ SDN plugin. To support a zero trust network policy, all components within the cluster should not be able to communicate with each other unless a Network Policy is configured. This requires the application of a policy to deny traffic within each project. A [default-deny.yml](baseline/default-deny.yml) NetworkPolicy is available which can be applied to each project to enforce this rule.


### Allowing Traffic Between Namespaces

Once the default NetworkPolicy of denying all traffic has been applied to each project, traffic from other namespaces will also be disabled. In certain cases, cross namespace communication is required in order for the operation of the components within OpenShift. In particular, traffic must be able to flow from the router deployed within the _default_ project and other namespaces. Network Policies can be applied to allow traffic from other namespaces based on namespace labels. 

Execute the following commands to label the namespaces which traffic will be originating from to support cross namespace communication

```
oc label namespace default name=default
oc label namespace default name=kube-service-catalog
```

Additional namespaces may be configured if desired.


### Allow Traffic from the Default Namespace

OpenShift provides a routing layer to external traffic to access applications within the cluster. Since traffic traverses through router(s) which are deployed within the _default_ namespace, a trust must be established between projects and the default namespace for traffic to flow properly. The NetworkPolicy [allow-from-default-namespace.yml](baseline/allow-from-default.yml) is available that should be applied to all projects.

### Configure Existing Projects

To enforce for projects which are configured during the installation of OpenShift have the same set of default policies to manage traffic , the following command can be executed:

```
for namespace in `oc get namespaces -o name`; do
oc apply -f baseline/default-deny.yml -n $namespace
oc apply -f baseline/allow-from-default-namespace.yml -n $namespace
done
```

### Default Policies for New Projects

In a prior section, Network Policies were applied to disable inter namespace communication while allowing access from the _default_ namespace to support ingress from the Router. These same set of policies can be applied for any new project that is created within OpenShift by [modifying the Default Project Template](https://docs.openshift.com/container-platform/latest/admin_guide/managing_projects.html#modifying-the-template-for-new-projects).

The following Ansible inventory content can be provided at cluster install time and placed within the `[OSEv3:vars]` group:

```
openshift_project_request_template_edits:
  - key: objects
    action: append
    value:
      kind: NetworkPolicy
      apiVersion: extensions/v1beta1
      metadata:
        name: default-deny
      spec:
        podSelector:
  - key: objects
    action: append
    value:
      kind: NetworkPolicy
      apiVersion: extensions/v1beta1
      metadata:
        name: allow-from-default-namespace
      spec:
        podSelector:
        ingress:
        - from:
          - namespaceSelector:
              matchLabels:
                name: default
```

## Configuration Automation

The set of default Network Policies as described in the sections above (with the exception of the default project template) can be automatically applied using Ansible. Use the following steps to complete the process:

1. Clone the repository

    ```
    git clone https://github.com/redhat-cop/openshift-toolkit
    ```

2. Change into the project directory and update Ansible dependencies

    ```
    cd openshift-toolkit/networkpolicy
    ansible-galaxy install -r requirements.yml -p playbooks/roles
    ```

3. Login to the OpenShift environment with a user with _cluster-admin_ privileges using the CLI

    ```
    oc login -u <username> https://<openshift-server>
    ```

4. Run the ansible playbook

The playbook performs the following tasks:

* Applies policies to targeted projects
* Applies default rules to all projects

To limit the items applied to the cluster based on the components installed in the cluster, the use of _openshift-applier_ `filter_tags` can be used. The following `filter_tags` are available:

* `default`
* `service-catalog`
* `logging`
* `metrics`

To avoid applying the set of default policies to all projects, the variable `apply_default_policies=false` can be specified.

To apply all policies, execute the following command:

```
 ansible-playbook -i inventory/ playbooks/apply-network-policies.yml
```

To apply _default_, _service-catalog_ and _logging_ policies along with a set of default policies to all projects, execute the folllowing command:

```
ansible-playbook -i inventory/ playbooks/apply-network-policies.yml -e filter_tags=default,service-catalog,logging
```

Finally, to avoid applying customized namespace policies through the _openshift-applier_, specify `skip_applier=true` as shown below:

```
ansible-playbook -i inventory/ playbooks/apply-network-policies.yml -e skip_applier=true
```