from kubernetes import client, config
from jsonpath_ng.ext import parse
import pytest

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
cv1 = client.CustomObjectsApi()


# Generic function #
def get_route_by_name(namespace, name):
    routes = cv1.list_namespaced_custom_object('route.openshift.io', 'v1',
                                               namespace, 'routes')
    jsonpath_expr = parse('items[?metadata.name == {}].$'.format(name))
    return [match.value for match in jsonpath_expr.find(routes)][0]


def get_running_pods_by_label(namespace, label):
    ret = v1.list_namespaced_pod(
        namespace, field_selector='status.phase=Running', label_selector=label)
    return len(ret.items)


def get_node_count():
    ret = v1.list_node()
    return len(ret.items)


# Master Test Section #
@pytest.mark.master
def test_master_controllers(master_node_count):
    assert get_running_pods_by_label(
        'kube-system', 'openshift.io/component=controllers') == int(master_node_count), \
        "Should have {} master controller pods".format(master_node_count)

@pytest.mark.master
def test_master_api(master_node_count):
    assert get_running_pods_by_label(
        'kube-system', 'openshift.io/component=api') == int(master_node_count), \
        "Should have {} master api pods".format(master_node_count)

@pytest.mark.master
def test_etcd(etcd_node_count):
    assert get_running_pods_by_label(
        'kube-system', 'openshift.io/component=etcd') == int(etcd_node_count), \
        "Should have {} etcd pods".format(etcd_node_count)


# Infra Test Section #
@pytest.mark.infra
def test_router(router_node_count):
    assert get_running_pods_by_label(
        'default', 'deploymentconfig=router') == int(router_node_count), \
        "Should have {} router pods".format(router_node_count)

@pytest.mark.infra
def test_registry(registry_pod_count):
    assert get_running_pods_by_label(
        'default', 'deploymentconfig=docker-registry') == int(registry_pod_count), \
        "Should have {} registry pods".format(registry_pod_count)


# Logging Test Section #
@pytest.mark.logging
def test_fluentd():
    assert get_running_pods_by_label(
        'openshift-logging', 'component=fluentd') == get_node_count(), \
        "Should have one fluentd pod for every node in the cluster"
