from kubernetes import client, config
from jsonpath_ng.ext import parse


# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
cv1 = client.CustomObjectsApi()


def getRouteByName(namespace, name):
    routes = cv1.list_namespaced_custom_object('route.openshift.io', 'v1',
                                               namespace, 'routes')
    jsonpath_expr = parse('items[?metadata.name == {}].$'.format(name))
    return [match.value for match in jsonpath_expr.find(routes)][0]


def getRunningPodsByLabel(namespace, label):
    ret = v1.list_namespaced_pod(
        namespace, field_selector='status.phase=Running', label_selector=label)
    return len(ret.items)


def getNodeCount():
    ret = v1.list_node()
    return len(ret.items)


def test_router():
    assert getRunningPodsByLabel(
        'default', 'deploymentconfig=router') == 3, "Should have 3 router pods"


def test_registry():
    assert getRunningPodsByLabel(
        'default', 'deploymentconfig=registry') == 3, "Should have 3 registry pods"


def test_etcd():
    assert getRunningPodsByLabel(
        'kube-system', 'openshift.io/component=etcd') == 3, "Should have 3 etcd pods"


def test_master_api():
    assert getRunningPodsByLabel(
        'kube-system', 'openshift.io/component=api') == 3, "Should have 3 master api pods"


def test_master_controllers():
    assert getRunningPodsByLabel(
        'kube-system', 'openshift.io/component=controllers') == 3, "Should have 3 master controller pods"


def test_fluentd():
    assert getRunningPodsByLabel(
        'openshift-logging', 'component=fluentd') == getNodeCount(), "Should have one fluentd pod for every node in the cluster"
