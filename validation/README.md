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

Use the default ansible hosts file, don't show the docker SHA256SUM, use the root user, or one with passwordless sudo to make ssh connections, check the repositories for OpenShift 3.11, check the nfs SELinux booleans and check that the default docker file has been edited because a private registry is being used

```./validate-pre-install.py --ansible-host-file=/etc/ansible/hosts --show-sha-sums=no --ansible-ssh-user=root --openshift-version=3.11 --nfs-booleans --private-registry```


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

If the cluster console being self-signed, ensure .kube/config has below entry
(`oc login --insecure-skip-tls-verify=true...`):
```
clusters:
- cluster:
    insecure-skip-tls-verify: true
    server: https://console.example.com:8443
  name: console-example-com:8443

```

Selection of test run:
1. Run all (default).
2. Skip selected test.
3. Run selected test.


#### 1. Run all (default)

* Run below command:

```
[root@mzali-fedora validation]# pytest -rs -v
=========================================================================================================================== test session starts ============================================================================================================================
platform linux2 -- Python 2.7.15, pytest-3.8.0, py-1.6.0, pluggy-0.7.1 -- /usr/bin/python2
cachedir: .pytest_cache
rootdir: /home/mzali/PycharmProjects/openshift-toolkit/validation, inifile: pytest.ini
collected 6 items

test_cluster_install.py::test_master_controllers PASSED                                                                                                                                                                                                              [ 16%]
test_cluster_install.py::test_master_api PASSED                                                                                                                                                                                                                      [ 33%]
test_cluster_install.py::test_etcd PASSED                                                                                                                                                                                                                            [ 50%]
test_cluster_install.py::test_router PASSED                                                                                                                                                                                                                          [ 66%]
test_cluster_install.py::test_registry PASSED                                                                                                                                                                                                                        [ 83%]
test_cluster_install.py::test_fluentd FAILED                                                                                                                                                                                                                         [100%]

================================================================================================================================= FAILURES =================================================================================================================================
_______________________________________________________________________________________________________________________________ test_fluentd _______________________________________________________________________________________________________________________________

    @pytest.mark.logging
    def test_fluentd():
>       assert k8s_client.get_running_pods_by_label(
            'openshift-logging', 'component=fluentd') == k8s_client.get_node_count(), \
            "Should have one fluentd pod for every node in the cluster"
E       AssertionError: Should have one fluentd pod for every node in the cluster
E       assert 0 == 3
E        +  where 0 = <bound method k8s_helper.get_running_pods_by_label of <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>>('openshift-logging', 'component=fluentd')
E        +    where <bound method k8s_helper.get_running_pods_by_label of <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>> = <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>.get_running_pods_by_label
E        +  and   3 = <bound method k8s_helper.get_node_count of <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>>()
E        +    where <bound method k8s_helper.get_node_count of <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>> = <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>.get_node_count

test_cluster_install.py:45: AssertionError
============================================================================================================================= warnings summary =============================================================================================================================
/usr/lib/python2.7/site-packages/urllib3/connectionpool.py:857: InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
  InsecureRequestWarning)

-- Docs: https://docs.pytest.org/en/latest/warnings.html
============================================================================================================== 1 failed, 5 passed, 1 warnings in 0.46 seconds ==============================================================================================================
Exception TypeError: "'NoneType' object is not callable" in <bound method ApiClient.__del__ of <kubernetes.client.api_client.ApiClient object at 0x7f9cd1392650>> ignored
Exception TypeError: "'NoneType' object is not callable" in <bound method ApiClient.__del__ of <kubernetes.client.api_client.ApiClient object at 0x7f9cd13b0ad0>> ignored
[root@mzali-fedora validation]#

```


#### 2. Skip selected test.

To skip some test, as this example, we want to skip `logging`.

* Edit pytest.ini, comment all `addopts` and left below addopts enabled:

```
[pytest]
# 1. Run all tests by default.
#addopts = --etcd-node-count=3 --router-node-count=2 --registry-pod-count=3 --master-node-count=3

# 2. Deselect test using marker. E.g skip logging test.
addopts = --etcd-node-count=3 --router-node-count=2 --registry-pod-count=3 --master-node-count=3 -k "not logging"

# 3. Run only test what marked with master or infra keyword. Ability to select certain test to run.
#addopts = --etcd-node-count=3 --router-node-count=3 --registry-pod-count=3 --master-node-count=3  -k "master or infra"

# 4. Debug purposes. To see which test will be selected to run
#addopts = --etcd-node-count=1 --router-node-count=1 --registry-pod-count=1 --master-node-count=1 --collect-only

```

* Run the test suite and we will see no `logging` test function will be called:
```
[root@mzali-fedora validation]# pytest -rs -v
=========================================================================================================================== test session starts ============================================================================================================================
platform linux2 -- Python 2.7.15, pytest-3.8.0, py-1.6.0, pluggy-0.7.1 -- /usr/bin/python2
cachedir: .pytest_cache
rootdir: /home/mzali/PycharmProjects/openshift-toolkit/validation, inifile: pytest.ini
collected 6 items / 1 deselected

test_cluster_install.py::test_master_controllers PASSED                                                                                                                                                                                                              [ 20%]
test_cluster_install.py::test_master_api PASSED                                                                                                                                                                                                                      [ 40%]
test_cluster_install.py::test_etcd PASSED                                                                                                                                                                                                                            [ 60%]
test_cluster_install.py::test_router PASSED                                                                                                                                                                                                                          [ 80%]
test_cluster_install.py::test_registry PASSED                                                                                                                                                                                                                        [100%]

============================================================================================================================= warnings summary =============================================================================================================================
/usr/lib/python2.7/site-packages/urllib3/connectionpool.py:857: InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
  InsecureRequestWarning)

-- Docs: https://docs.pytest.org/en/latest/warnings.html
============================================================================================================ 5 passed, 1 deselected, 1 warnings in 0.33 seconds ============================================================================================================
Exception TypeError: "'NoneType' object is not callable" in <bound method ApiClient.__del__ of <kubernetes.client.api_client.ApiClient object at 0x7f077f229650>> ignored
Exception TypeError: "'NoneType' object is not callable" in <bound method ApiClient.__del__ of <kubernetes.client.api_client.ApiClient object at 0x7f077f247ad0>> ignored
[root@mzali-fedora validation]#

```

#### 3. Run selected test.

* There are occasion we want just to run selected test. As example here we want only test has being
marked as `master` and `infra` test function.

* Edit pytest.ini and only enable below line:
```
[pytest]
# 1. Run all tests by default.
#addopts = --etcd-node-count=1 --router-node-count=1 --registry-pod-count=1 --master-node-count=1

# 2. Deselect test using marker. E.g skip logging test.
#addopts = --etcd-node-count=1 --router-node-count=1 --registry-pod-count=1 --master-node-count=1 -k "not logging"

# 3. Run only test what marked with master or infra keyword. Ability to select certain test to run.
addopts = --etcd-node-count=3 --router-node-count=3 --registry-pod-count=3 --master-node-count=3  -k "master or infra"

# 4. Debug purposes. To see which test will be selected to run
#addopts = --etcd-node-count=1 --router-node-count=1 --registry-pod-count=1 --master-node-count=1 --collect-only
```

* Run the test:
```
[root@mzali-fedora validation]# pytest -rs -v
=========================================================================================================================== test session starts ============================================================================================================================
platform linux2 -- Python 2.7.15, pytest-3.8.0, py-1.6.0, pluggy-0.7.1 -- /usr/bin/python2
cachedir: .pytest_cache
rootdir: /home/mzali/PycharmProjects/openshift-toolkit/validation, inifile: pytest.ini
collected 6 items / 3 deselected

test_cluster_install.py::test_master_controllers PASSED                                                                                                                                                                                                              [ 33%]
test_cluster_install.py::test_master_api PASSED                                                                                                                                                                                                                      [ 66%]
test_cluster_install.py::test_etcd PASSED                                                                                                                                                                                                                            [100%]

============================================================================================================================= warnings summary =============================================================================================================================
/usr/lib/python2.7/site-packages/urllib3/connectionpool.py:857: InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
  InsecureRequestWarning)

-- Docs: https://docs.pytest.org/en/latest/warnings.html
============================================================================================================ 3 passed, 3 deselected, 1 warnings in 0.32 seconds ============================================================================================================
Exception TypeError: "'NoneType' object is not callable" in <bound method ApiClient.__del__ of <kubernetes.client.api_client.ApiClient object at 0x7fed4014a650>> ignored
Exception TypeError: "'NoneType' object is not callable" in <bound method ApiClient.__del__ of <kubernetes.client.api_client.ApiClient object at 0x7fed40168ad0>> ignored
[root@mzali-fedora validation]#

```

#### How to determined if test failed?

1.Look for assertion error:
```
_______________________________________________________________________________________________________________________________ test_fluentd _______________________________________________________________________________________________________________________________

    @pytest.mark.logging
    def test_fluentd():
>       assert k8s_client.get_running_pods_by_label(
            'openshift-logging', 'component=fluentd') == k8s_client.get_node_count(), \
            "Should have one fluentd pod for every node in the cluster"
E       AssertionError: Should have one fluentd pod for every node in the cluster
E       assert 0 == 3
E        +  where 0 = <bound method k8s_helper.get_running_pods_by_label of <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>>('openshift-logging', 'component=fluentd')
E        +    where <bound method k8s_helper.get_running_pods_by_label of <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>> = <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>.get_running_pods_by_label
E        +  and   3 = <bound method k8s_helper.get_node_count of <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>>()
E        +    where <bound method k8s_helper.get_node_count of <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>> = <validation.lib.k8s_helper.k8s_helper instance at 0x7f9cd1427b00>.get_node_count

test_cluster_install.py:45: AssertionError
============================================================================================================================= warnings summary =============================================================================================================================
```

or,

2.Look at the summary:
```
test_cluster_install.py::test_master_controllers PASSED                                                                                                                                                                                                              [ 16%]
test_cluster_install.py::test_master_api PASSED                                                                                                                                                                                                                      [ 33%]
test_cluster_install.py::test_etcd PASSED                                                                                                                                                                                                                            [ 50%]
test_cluster_install.py::test_router PASSED                                                                                                                                                                                                                          [ 66%]
test_cluster_install.py::test_registry PASSED                                                                                                                                                                                                                        [ 83%]
test_cluster_install.py::test_fluentd FAILED
```
