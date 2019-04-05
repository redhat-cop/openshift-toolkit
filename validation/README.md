# OpenShift Cluster Validation

## Pre Install Validation

A script that is used to check that the prerequisites for OpenShift Container Platform are present within the target environment

```
Usage: validate-pre-install.py [options]

Options:
  -h, --help            show this help message and exit
  --ansible-host-file=ANSIBLE_HOST_FILE
                        Specify location of ansible hostfile
  --show-sha-sums=SHOW_SHA_SUMS
                        Toggle whether or not to show the sha sum of files on
                        remote host
  --ansible-ssh-user=ANSIBLE_SSH_USER
                        Which user will ansible be run as
  --openshift-version=OPENSHIFT_VERSION
                        The version of openshift to check against
  --private-registry    Indicates whether or not you are using a private
                        registry for installation
  --nfs-booleans        Indicate whether or not to check fornfs selinux
                        booleans.
```

### Sample Usage:

Use the default ansible hosts file, don't show the docker SHA256SUM, use the root user to make ssh connections, check the repositories for OpenShift 3.3, check the nfs SELinux booleans and check that the default docker file has been edited because a private registry is being used

```./validate-pre-install.py --ansible-host-file=/etc/ansible/hosts --show-sha-sums=no --ansible-ssh-user=root --openshift-version=3.3 --nfs-booleans --private-registry```


The script will output the follow information during runtime:

```Attempting to make a remote SSH connection to: master02.ose.example.com
Checking to see if ['virt_sandbox_use_nfs', 'virt_use_nfs'] are turned on...
Checking to see if /var/lib/etcd is a partition...
Running 'yum list installed' on master02.ose.example.com...
Running 'yum list updates' on master02.ose.example.com...
Running 'sestatus' on master02.ose.example.com
Running 'systemctl status docker' on master02.ose.example.com...
Running 'subscription-manager status' on master02.ose.example.com...
Running 'subscription-manager repos' on master02.ose.example.com...
Attempting to forward lookup of master02.ose.example.com...
Attempting to reverse lookup of master02.ose.example.com...
```

After the script has completed a colourized, text based, tab formatted report is generated.

* Words in YELLOW are warnings, these are no show stoppers but are worth paying attention to.
* Words in GREEN have passed the checks appropriately
* Words in RED are failures that need to be addressed before the installation may proceed

## Post Install State Validation

For validating that an installed cluster is in the expected state, we've written a set of [Pytest](https://docs.pytest.org/en/latest/) test cases. They can be run with the following:

Below pre-req must be run first before the pytest framework being executed:

```
pip install -r requirements.txt
oc login ...
```

To run test that include `master` and `infra`:

Edit pytest.ini  or run `pytest` with following options

```
pytest  --etcd-node-count=3 --router-node-count=2 --registry-pod-count=3 --master-node-count=3  -k "master or infra"
```

The tests will output test successes and failures, for example...
```
____________________________________ test_masters ____________________________________

    def test_etcd():
>       assert getRunningPodsByLabel(
            'kube-system', 'openshift.io/component=etcd') == 3, "Should have 3 etcd pods"
E       AssertionError: Should have 3 etcd pods
E       assert 1 == 3
E        +  where 1 = getRunningPodsByLabel('kube-system', 'openshift.io/component=etcd')

test_cluster_install.py:31: AssertionError

======================= 3 failed, 1 passed, 1 warnings in 1.12 seconds =======================
```
