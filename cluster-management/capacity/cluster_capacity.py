#!/usr/bin/env python3
from kubernetes import client, config

k8s_sizing = {
    'Ti': 1024 ** 4,
    'T': 1000 ** 4,
    'Gi': 1024 ** 3,
    'G': 1000 ** 3,
    'Mi': 1024 ** 2,
    'M': 1000 ** 0,
    'Ki': 1024 ** 1,
    'K': 1000 ** 1,
}


def mem_to_bytes(k8s_size):
    unit = ''.join(filter(lambda x: x.isalpha(), k8s_size))
    size = int(k8s_size.rstrip(unit))
    try:
        return size * k8s_sizing[unit.capitalize()]
    except KeyError:
        return size


def mem_from_bytes(size_bytes, unit):
    return size_bytes / k8s_sizing[unit]


def cpu_to_cores(size):
    try:
        return int(size)
    except ValueError:
        size = size.rstrip('m')
        return int(size) / 1000


# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()


v1 = client.CoreV1Api()


def get_request_limit_totals():
    ret = v1.list_pod_for_all_namespaces(watch=False)

    mem_requests = 0
    mem_limits = 0
    cpu_requests = 0
    cpu_limits = 0

    for pod in ret.items:
        for c in pod.spec.containers:
            if c.resources.limits is not None:
                if "cpu" in c.resources.limits:
                    cpu_limits += cpu_to_cores(c.resources.limits["cpu"])
                if "memory" in c.resources.limits:
                    mem_limits += mem_to_bytes(
                        c.resources.limits["memory"])
            if c.resources.requests is not None:
                if "cpu" in c.resources.requests:
                    cpu_requests += cpu_to_cores(
                        c.resources.requests["cpu"])
                if "memory" in c.resources.requests:
                    mem_requests += mem_to_bytes(
                        c.resources.requests["memory"])
    return cpu_requests, cpu_limits, mem_requests, mem_limits


def get_cluster_capacity():
    cpu_a = 0
    mem_a = 0

    ret = v1.list_node()
    for node in ret.items:
        cpu_a += cpu_to_cores(node.status.allocatable["cpu"])
        mem_a += mem_to_bytes(node.status.allocatable["memory"])

    return cpu_a, mem_a


total_cpu_requests, total_cpu_limits, total_mem_requests, total_mem_limits = get_request_limit_totals()
total_cpu, total_memory = get_cluster_capacity()
print()
for args in (
            ('CPU Requests', 'CPU Limits', 'Memory Requests', 'Memory Limits'),
            ('------------', '----------', '---------------', '-------------'),
            (
                '{} Cores ({:.0%})'.format(
                                    str(total_cpu_requests),
                                    total_cpu_requests / total_cpu
                                    ),
                '{} Cores ({:.0%})'.format(
                                    str(total_cpu_limits),
                                    total_cpu_limits / total_cpu
                                    ),
                '{}Gi ({:.0%})'.format(
                                    str(mem_from_bytes(total_mem_requests, 'Gi')),
                                    total_mem_requests / total_memory
                                    ),
                '{}Gi ({:.0%})'.format(
                                    str(mem_from_bytes(total_mem_limits, 'Gi')),
                                    total_mem_limits / total_memory
                                    )
            )
        ):
    print('{0:<30} {1:<30} {2:<30} {3:<30}'.format(*args))
