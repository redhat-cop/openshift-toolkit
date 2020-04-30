from .lib import k8sHelper
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
def test_master_etcd(etcd_node_count):
    assert k8s_client.get_running_pods_by_label(
        'kube-system', 'openshift.io/component=etcd') == int(etcd_node_count), \
        "Should have {} etcd pods".format(etcd_node_count)


# Infra Test Section #
@pytest.mark.infra
def test_infra_router(router_node_count):
    assert k8s_client.get_running_pods_by_label(
        'default', 'deploymentconfig=router') == int(router_node_count), \
        "Should have {} router pods".format(router_node_count)


@pytest.mark.infra
def test_infra_registry(registry_pod_count):
    assert k8s_client.get_running_pods_by_label(
        'default', 'deploymentconfig=docker-registry') == int(registry_pod_count), \
        "Should have {} registry pods".format(registry_pod_count)


# Logging Test Section #
@pytest.mark.logging
def test_logging_fluentd():
    assert k8s_client.get_running_pods_by_label(
        'openshift-logging', 'component=fluentd') == k8s_client.get_node_count(), \
        "Should have one fluentd pod for every node in the cluster"


@pytest.mark.logging
def test_logging_elasticsearch(es_pod_count):
    assert k8s_client.get_running_pods_by_label(
        'openshift-logging', 'component=es') >= int(es_pod_count), \
        "Should have {} Elasticsearch pod in the cluster".format(es_pod_count)


@pytest.mark.logging
def test_logging_kibana(kibana_pod_count):
    assert k8s_client.get_running_pods_by_label(
        'openshift-logging', 'component=kibana') == int(kibana_pod_count), \
        "Should have {} Kibana pod in the cluster".format(kibana_pod_count)


# Monitoring Test Section #
@pytest.mark.monitoring
def test_monitoring_node_exporter():
    assert k8s_client.get_running_pods_by_label(
        'openshift-monitoring', 'app=node-exporter') == k8s_client.get_node_count(), \
        "Should have {} fluentd pod in the cluster as total number of node is {}.".format(k8s_client.get_node_count())


@pytest.mark.monitoring
def test_monitoring_prometheus(prom_pod_count):
    assert k8s_client.get_running_pods_by_label(
        'openshift-monitoring', 'app=prometheus') == int(prom_pod_count), \
        "Should have {} prometheus pod in the cluster".format(prom_pod_count)


@pytest.mark.monitoring
def test_monitoring_alertmanager(alertmanager_pod_count):
    assert k8s_client.get_running_pods_by_label(
        'openshift-monitoring', 'app=alertmanager') == int(alertmanager_pod_count), \
        "Should have {} alertmanager pod in the cluster".format(alertmanager_pod_count)


@pytest.mark.monitoring
def test_monitoring_grafana(grafana_pod_count):
    assert k8s_client.get_running_pods_by_label(
        'openshift-monitoring', 'app=grafana') == int(grafana_pod_count), \
        "Should have {} grafana pod in the cluster".format(grafana_pod_count)


@pytest.mark.monitoring
def test_monitoring_kube_state_metrics(kube_state_metrics_pod_count):
    assert k8s_client.get_running_pods_by_label(
        'openshift-monitoring', 'app=kube-state-metrics') == int(kube_state_metrics_pod_count), \
        "Should have {} kube-state-metrics pod in the cluster".format(kube_state_metrics_pod_count)
