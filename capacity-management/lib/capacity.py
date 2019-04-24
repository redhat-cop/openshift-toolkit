from kubernetes import client, config
from lib import convert
import warnings


# Configs can be set in Configuration class directly or using helper utility
warnings.simplefilter("ignore")
config.load_kube_config()
v1 = client.CoreV1Api()


def get_cluster_capacity():
    cpu_a = 0
    mem_a = 0

    nodes = {}

    ret = v1.list_node()
    for node in ret.items:
        nodes[node.metadata.name] = {
            "cpu": node.status.allocatable["cpu"], "memory": node.status.allocatable["memory"]}
        cpu_a += convert.cpu_to_cores(node.status.allocatable["cpu"])
        mem_a += convert.mem_to_bytes(node.status.allocatable["memory"])

    nodes["totals"] = {"cpu": cpu_a, "memory": mem_a}
    return nodes


def get_cluster_resource_quota():
    cpu = 0
    mem = 0

    quota_data = {
        "cpu": "",
        "memory": "",
        "namespaces": {}
    }

    ret = v1.list_resource_quota_for_all_namespaces()
    for quota in ret.items:
        namespace = quota.metadata.namespace
        q_cpu = convert.cpu_to_cores(quota.spec.hard["cpu"])
        q_mem = convert.mem_to_bytes(quota.spec.hard["memory"])

        # Ensure we only count one quota for a namesapce
        if namespace not in quota_data:
            cpu += q_cpu
            mem += q_mem
            quota_data["namespaces"][namespace] = {
                "cpu": q_cpu, "memory": q_mem}
            continue

        # There are multiple quotas, let's count the one for non terminating pods
        #  we also need to remember to subtract the value we're replacing from the totals
        if quota.spec.scopes and "NotTerminating" in quota.spec.scopes:
            cpu += q_cpu - quota_data[namespace]["cpu"]
            mem += q_mem - quota_data[namespace]["memory"]

    quota_data.update({"cpu": cpu, "memory": mem})
    return quota_data


def get_request_limit_totals():
    ret = v1.list_pod_for_all_namespaces(watch=False)

    mem_requests = 0
    mem_limits = 0
    cpu_requests = 0
    cpu_limits = 0

    rl_data = {
        "requests": {
            "cpu": "",
            "memory": "",
        },
        "limits": {
            "cpu": "",
            "memory": "",
        },
        "namespaces": {}
    }

    for pod in ret.items:
        # Ignore pods that aren't running
        if pod.status.phase != "Running":
            continue

        if pod.metadata.namespace not in rl_data["namespaces"]:
            rl_data["namespaces"].update({pod.metadata.namespace: {}})

        pod_data = {
            pod.metadata.name: {}
        }

        for c in pod.spec.containers:

            if c.resources is None:
                continue

            c_data = {
                "requests": {},
                "limits": {}
            }

            if c.resources.limits is not None:
                if "cpu" in c.resources.limits:
                    c_data["limits"]["cpu"] = convert.cpu_to_cores(
                        c.resources.limits["cpu"])
                    cpu_limits += convert.cpu_to_cores(
                        c.resources.limits["cpu"])
                if "memory" in c.resources.limits:
                    c_data["limits"]["memory"] = convert.mem_to_bytes(
                        c.resources.limits["memory"])
                    mem_limits += convert.mem_to_bytes(
                        c.resources.limits["memory"])
            if c.resources.requests is not None:
                if "cpu" in c.resources.requests:
                    c_data["requests"]["cpu"] = convert.cpu_to_cores(
                        c.resources.requests["cpu"])
                    cpu_requests += convert.cpu_to_cores(
                        c.resources.requests["cpu"])
                if "memory" in c.resources.requests:
                    c_data["requests"]["memory"] = convert.mem_to_bytes(
                        c.resources.requests["memory"])
                    mem_requests += convert.mem_to_bytes(
                        c.resources.requests["memory"])

            if c_data:
                pod_data[pod.metadata.name].update({c.name: c_data})

        if pod_data:
            rl_data["namespaces"][pod.metadata.namespace].update(pod_data)

    rl_data["requests"]["totals"] = {
        "cpu": cpu_requests, "memory": mem_requests}
    rl_data["limits"]["totals"] = {"cpu": cpu_limits, "memory": mem_limits}
    return rl_data


def get_capacity_data():
    capacity = {}
    capacity["cluster"] = get_cluster_capacity()
    capacity["quota"] = get_cluster_resource_quota()
    capacity.update(get_request_limit_totals())

    return capacity
