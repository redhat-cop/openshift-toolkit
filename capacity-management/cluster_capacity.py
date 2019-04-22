#!/usr/bin/env python3
from kubernetes import client, config
from lib import convert

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
v1 = client.CoreV1Api()


def get_cluster_capacity():
    cpu_a = 0
    mem_a = 0

    ret = v1.list_node()
    for node in ret.items:
        cpu_a += convert.cpu_to_cores(node.status.allocatable["cpu"])
        mem_a += convert.mem_to_bytes(node.status.allocatable["memory"])

    return cpu_a, mem_a


def get_cluster_resource_quota():
    cpu = 0
    mem = 0

    ret = v1.list_resource_quota_for_all_namespaces()
    for quota in ret.items:
        if quota.spec.scopes and "NotTerminating" in quota.spec.scopes:
            cpu += convert.cpu_to_cores(quota.spec.hard["cpu"])
            mem += convert.mem_to_bytes(quota.spec.hard["memory"])

    return cpu, mem


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
                    cpu_limits += convert.cpu_to_cores(
                        c.resources.limits["cpu"])
                if "memory" in c.resources.limits:
                    mem_limits += convert.mem_to_bytes(
                        c.resources.limits["memory"])
            if c.resources.requests is not None:
                if "cpu" in c.resources.requests:
                    cpu_requests += convert.cpu_to_cores(
                        c.resources.requests["cpu"])
                if "memory" in c.resources.requests:
                    mem_requests += convert.mem_to_bytes(
                        c.resources.requests["memory"])
    return cpu_requests, cpu_limits, mem_requests, mem_limits


total_cpu, total_memory = get_cluster_capacity()
total_quota_cpu, total_quota_mem = get_cluster_resource_quota()
total_cpu_requests, total_cpu_limits, total_mem_requests, total_mem_limits = get_request_limit_totals()
memory_unit = 'Gi'

print()
print('Total Cluster Size:')
print('----')
print('\tMemory:\t{} {}'.format(convert.mem_from_bytes(
    total_memory, memory_unit), memory_unit))
print('\tCPU:\t{} Cores'.format(total_cpu))
print()
print('Amount Claimed By Quota:')
print('----')
print('\tMemory:\t{} {} ({}%)'.format(convert.mem_from_bytes(
    total_quota_mem, memory_unit), memory_unit, total_quota_mem/total_memory*100))
print('\tCPU:\t{} Cores ({}%)'.format(
    total_quota_cpu, total_quota_cpu/total_cpu*100))
print()
print('Total Limits:')
print('----')
print('\tMemory:\t{} {} ({}%)'.format(convert.mem_from_bytes(
    total_mem_limits, memory_unit), memory_unit, total_mem_limits/total_memory*100))
print('\tCPU:\t{} Cores ({}%)'.format(
    total_cpu_limits, total_cpu_limits/total_cpu*100))
print()
print('Total Requests:')
print('----')
print('\tMemory:\t{} {} ({}%)'.format(convert.mem_from_bytes(
    total_mem_requests, memory_unit), memory_unit, total_mem_requests/total_memory*100))
print('\tCPU:\t{} Cores ({}%)'.format(
    total_cpu_requests, total_cpu_requests/total_cpu*100))
