import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--master-node-count", action="store", default=3, help = "Master node count."
    )
    parser.addoption(
        "--etcd-node-count", action="store", default=3, help="ectd node count."
    )
    parser.addoption(
        "--router-node-count", action="store", default=3, help = "Router node count."
    )
    parser.addoption(
        "--registry-pod-count", action="store", default=3, help = "Registry pod count."
    )

@pytest.fixture
def master_node_count(request):
    return request.config.getoption("--master-node-count")


@pytest.fixture
def etcd_node_count(request):
    return request.config.getoption("--etcd-node-count")


@pytest.fixture
def router_node_count(request):
    return request.config.getoption("--router-node-count")


@pytest.fixture
def registry_pod_count(request):
    return request.config.getoption("--registry-pod-count")


