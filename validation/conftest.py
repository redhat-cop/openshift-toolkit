import pytest


def pytest_addoption(parser):
    # Master option section
    parser.addoption(
        "--master-node-count", action="store", default=3, help="Master node count."
    )
    parser.addoption(
        "--etcd-node-count", action="store", default=3, help="ectd node count."
    )
    # Infra option section
    parser.addoption(
        "--router-node-count", action="store", default=3, help="Router node count."
    )
    parser.addoption(
        "--registry-pod-count", action="store", default=3, help="Registry pod count."
    )
    # Logging option section
    parser.addoption(
        "--es-pod-count", action="store", default=3, help="Elasticsearch pod count."
    )
    parser.addoption(
        "--kibana-pod-count", action="store", default=1, help="Kibana pod count."
    )
    # Monitoring option section
    parser.addoption(
        "--prom-pod-count", action="store", default=2, help="Prometheus pod count."
    )
    parser.addoption(
        "--alertmanager-pod-count", action="store", default=2, help="Alertmanager pod count."
    )
    parser.addoption(
        "--grafana-pod-count", action="store", default=1, help="Grafana pod count."
    )
    parser.addoption(
        "--kube-state-metrics-pod-count", action="store", default=1, help="kube-state-metrics pod count."
    )


# Master fixtures
@pytest.fixture
def master_node_count(request):
    return request.config.getoption("--master-node-count")


@pytest.fixture
def etcd_node_count(request):
    return request.config.getoption("--etcd-node-count")


# Infra fixtures
@pytest.fixture
def router_node_count(request):
    return request.config.getoption("--router-node-count")


@pytest.fixture
def registry_pod_count(request):
    return request.config.getoption("--registry-pod-count")


# Logging fixtures
@pytest.fixture
def es_pod_count(request):
    return request.config.getoption("--es-pod-count")


@pytest.fixture
def kibana_pod_count(request):
    return request.config.getoption("--kibana-pod-count")


# Monitoring fixtures
@pytest.fixture
def prom_pod_count(request):
    return request.config.getoption("--prom-pod-count")


@pytest.fixture
def alertmanager_pod_count(request):
    return request.config.getoption("--alertmanager-pod-count")


@pytest.fixture
def grafana_pod_count(request):
    return request.config.getoption("--grafana-pod-count")


@pytest.fixture
def kube_state_metrics_pod_count(request):
    return request.config.getoption("--kube-state-metrics-pod-count")