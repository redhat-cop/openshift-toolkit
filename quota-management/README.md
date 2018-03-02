# Sample Quota Management Strategy for OpenShift

The following is an example of a strategy that might be employed by an Operations team for managing project quotas. This approach uses the concept of _tier profiles_ so as to avoid having to manage many custom quotas for each project/tenant. In this example we have defined the following tier profiles.

| Profile | Project CPU             | Project Memory          | Per Pod CPU                       | Per Pod Memory                         |
|---------|-------------------------|-------------------------|-----------------------------------|----------------------------------------|
| Small (default)  | 1 core (burstable to 2) | 6 Gi (burstable to 8)   | 10m - 100m; default request: 50m  | 128 Mi - 1 Gi; default request: 256 Mi |
| Medium  | 2 core (burstable to 4) | 12 Gi (burstable to 16) | 10m - 200m; default request: 50m  | 128 Mi - 2 Gi; default request: 256 Mi |
| Large   | 4 core (burstable to 8) | 24 Gi (burstable to 32) | 10m - 1000m; default request: 50m | 128 Mi - 4 Gi; default request: 256 Mi |

The specs above are not important, nor are the number of profiles we've defined. What is important is how we define & apply the quotas to projects. We describe the process below.

## Concepts and Workflow

The following sections describe how we piece together this approach.

### Quota Files

First off, each quota is defined in its own YAML file (`./files/quota-small.yml`, `./files/quota-medium.yml`, `./files/quota-large.yml`) in a git repo. Each file contains the same _List_ of objects all with the same names:

```
$ awk '/name:/{print}' files/quota-*.yml
files/quota-large.yml:    name: quota
files/quota-large.yml:    name: burst-quota
files/quota-large.yml:    name: limits
files/quota-medium.yml:    name: quota
files/quota-medium.yml:    name: burst-quota
files/quota-medium.yml:    name: limits
files/quota-small.yml:    name: quota
files/quota-small.yml:    name: burst-quota
files/quota-small.yml:    name: limits
```

The _profiles_ are differentiated using labels and annotations:

```
$ awk /'labels:/{getline; print}' files/quota-*.yml
      quota-tier: Large
      quota-tier: Large
      quota-tier: Large
      quota-tier: Medium
      quota-tier: Medium
      quota-tier: Medium
      quota-tier: Small
      quota-tier: Small
      quota-tier: Small

$ awk /'annotations:/{getline; print}' files/quota-*.yml
      openshift.io/quota-tier: Large
      openshift.io/quota-tier: Large
      openshift.io/quota-tier: Large
      openshift.io/quota-tier: Medium
      openshift.io/quota-tier: Medium
      openshift.io/quota-tier: Medium
      openshift.io/quota-tier: Small
      openshift.io/quota-tier: Small
      openshift.io/quota-tier: Small
```

### Apply Quota Tier Profiles

When set up as above, our _tier profiles_ may be easily applied, reapplied, and overlayed on top of each other. Let's look at an example.

A user wants to create a new project, and does so via `oc new-project myapp-space`.

A `cluster-admin` can then simply go in and apply the small quota to that project in order to limit resource consumption in that new project.

```
$ oc apply -f files/quota-small.yml -n myapp-space
resourcequota "quota" created
resourcequota "burst-quota" created
limitrange "limits" created
```

Looking at the resources created, we can see the consistent `quota-tier=Small` label across them.

```
$ oc get quota,limitrange --show-labels -n myapp-space
NAME                AGE       LABELS
quota/burst-quota   2m        quota-tier=Small
quota/quota         2m        quota-tier=Small

NAME            AGE       LABELS
limits/limits   2m        quota-tier=Small
```

Now let's create a couple more projects all with a small quota.

```
$ oc new-project myapp-space2
$ oc apply -f files/quota-small.yml -n myapp-space2
$ oc new-project myapp-space3
$ oc apply -f files/quota-small.yml -n myapp-space3
$ oc new-project myapp-space4
$ oc apply -f files/quota-small.yml -n myapp-space4
```

And now, let's re-examine what we've got as far as quotas established.

```
$ oc get quota,limitrange --all-namespaces --show-labels
NAMESPACE      NAME                AGE       LABELS
myapp-space    quota/burst-quota   14m       quota-tier=Small
myapp-space    quota/quota         14m       quota-tier=Small
myapp-space2   quota/burst-quota   3m        quota-tier=Small
myapp-space2   quota/quota         3m        quota-tier=Small
myapp-space3   quota/burst-quota   2m        quota-tier=Small
myapp-space3   quota/quota         2m        quota-tier=Small
myapp-space4   quota/burst-quota   2m        quota-tier=Small
myapp-space4   quota/quota         2m        quota-tier=Small

NAMESPACE      NAME            AGE       LABELS
myapp-space    limits/limits   14m       quota-tier=Small
myapp-space2   limits/limits   2m        quota-tier=Small
myapp-space3   limits/limits   2m        quota-tier=Small
myapp-space4   limits/limits   2m        quota-tier=Small
```

As you can see, we have 4 projects, each with our Small _tier profile_ applied to it.

Now let's say that `myapp-space2` is consistently running up against it's quota, and we would like to grant it some more breathing room. Doing that is as easy as applying a larger _tier profile_ to the project.

```
$ oc apply -f files/quota-medium.yml -n myapp-space2
resourcequota "quota" configured
resourcequota "burst-quota" configured
limitrange "limits" configured
```

Notice that this time around the same 3 objects are listed, but they are listed as `configured` instead of `created`. This is because our _tier profiles_ all define the same set of named resources, just with different values. If we look at the labels, we can, in fact see that the objects were updated.

```
$ oc get quota,limitrange --all-namespaces --show-labels
NAMESPACE      NAME                AGE       LABELS
myapp-space    quota/burst-quota   23m       quota-tier=Small
myapp-space    quota/quota         23m       quota-tier=Small
myapp-space2   quota/burst-quota   12m       quota-tier=Medium
myapp-space2   quota/quota         12m       quota-tier=Medium
myapp-space3   quota/burst-quota   11m       quota-tier=Small
myapp-space3   quota/quota         11m       quota-tier=Small
myapp-space4   quota/burst-quota   11m       quota-tier=Small
myapp-space4   quota/quota         11m       quota-tier=Small

NAMESPACE      NAME            AGE       LABELS
myapp-space    limits/limits   23m       quota-tier=Small
myapp-space2   limits/limits   11m       quota-tier=Medium
myapp-space3   limits/limits   11m       quota-tier=Small
myapp-space4   limits/limits   10m       quota-tier=Small
```

Just for the sake of experimentation, let's also apply the Large profile to a project.

```
$ oc apply -f files/quota-large.yml -n myapp-space4
resourcequota "quota" configured
resourcequota "burst-quota" configured
limitrange "limits" configured
$ oc get quota,limitrange --all-namespaces --show-labels
NAMESPACE      NAME                AGE       LABELS
myapp-space    quota/burst-quota   25m       quota-tier=Small
myapp-space    quota/quota         25m       quota-tier=Small
myapp-space2   quota/burst-quota   14m       quota-tier=Medium
myapp-space2   quota/quota         14m       quota-tier=Medium
myapp-space3   quota/burst-quota   14m       quota-tier=Small
myapp-space3   quota/quota         14m       quota-tier=Small
myapp-space4   quota/burst-quota   13m       quota-tier=Large
myapp-space4   quota/quota         13m       quota-tier=Large

NAMESPACE      NAME            AGE       LABELS
myapp-space    limits/limits   25m       quota-tier=Small
myapp-space2   limits/limits   14m       quota-tier=Medium
myapp-space3   limits/limits   13m       quota-tier=Small
myapp-space4   limits/limits   13m       quota-tier=Large
```

## Automating the Solution

This section describes a few ways we can advance the solution through advanced configuration and automation.

### (Recommended) Add the desired default Profile to the default project template

OpenShift allows cluster administrators to customize the default template that is used to create projects when a user runs `oc new-project`. That process is described further in the [OpenShift Documentation](https://docs.openshift.com/container-platform/latest/admin_guide/managing_projects.html#modifying-the-template-for-new-projects).

In order to lower the overhead in our process, we can embed the Small _tier profile_ in our cluster's default project template. This way, every project that gets created will, by default, be restrcted by a small quota. An example of what this default project template looks like can be found in `files/default-project-template.yml`.

With that template applied and configured, this ensures that all projects in our cluster will automatically be created with a small default quota. Now, the only action that needs to be taken by an administrator is to update a project to a larger quota.

### (Recommended) Automate the process further using the openshift-applier

The [openshift-applier](https://github.com/redhat-cop/casl-ansible/tree/master/roles/openshift-applier) is an ansible role that supports declarative automation for rolling out OpenShift resources. This role can be used to declare a set of projects and their quotas, and keep them up to date with ansible. Here's a sample of how you would define the ansible variables to accomplish this.

```
openshift_cluster_content:
- object: quotas
  content:
  - name: "myapp-space2"
    file: "files/quota-medium.yml"
    namespace: "myapp-space2"
  - name: "my-space4"
    file: "files/quota-large.yml"
    namespace: "myapp-space4"
```

NOTE: Because we've already inserted the Small profile in our default project template, we only need to declare quotas for the projects that need something beyond the default quota.

A full sample inventory can be found at `./inventory/`. A sample ansible run might look like:

```
ansible-playbook -i ./inventory/ /path/to/casl-ansible/playbooks/openshift-cluster-seed.yml
```

### (Optional) Use git pull requests to establish a lightweight quota request workflow

With all of our assets that define and manage quota defined in code and automatically rolled out with ansible, its very easy to open this code up to the rest of the organization to request changes to quotas. We can simply establish a new git repository containing this content, and set it as readable by the entire org, writeable only by an operations team, and allow the rest of the org to fork the repo and open Pull Requests/Merge Requests to have their quota modified.
