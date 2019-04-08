from lib import k8sHelper
import pytest

# Instantiate k8s_helper class from k8s_helper library.
k8s_client = k8sHelper.k8sHelper()


# Master Test Section #
@pytest.mark.master
def test_master_controllers(master_node_count):
    assert k8s_client.get_running_pods_by_label(
        'kube-system', 'openshift.io/component=controllers') == int(master_node_count), \
        "Should have {} master controller pods".format(master_node_count)


@pytest.mark.master
def test_master_api(master_node_count):
    assert k8s_client.get_running_pods_by_label(
        'kube-system', 'openshift.io/component=api') == int(master_node_count), \
        "Should have {} master api pods".format(master_node_count)


@pytest.mark.master
def test_etcd(etcd_node_count):
    assert k8s_client.get_running_pods_by_label(
        'kube-system', 'openshift.io/component=etcd') == int(etcd_node_count), \
        "Should have {} etcd pods".format(etcd_node_count)


# Infra Test Section #
@pytest.mark.infra
def test_router(router_node_count):
    assert k8s_client.get_running_pods_by_label(
        'default', 'deploymentconfig=router') == int(router_node_count), \
        "Should have {} router pods".format(router_node_count)


@pytest.mark.infra
def test_registry(registry_pod_count):
    assert k8s_client.get_running_pods_by_label(
        'default', 'deploymentconfig=docker-registry') == int(registry_pod_count), \
        "Should have {} registry pods".format(registry_pod_count)


# Logging Test Section #
@pytest.mark.logging
def test_fluentd():
    assert k8s_client.get_running_pods_by_label(
        'openshift-logging', 'component=fluentd') == k8s_client.get_node_count(), \
        "Should have one fluentd pod for every node in the cluster"
