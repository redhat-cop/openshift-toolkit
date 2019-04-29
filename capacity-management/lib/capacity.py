from kubernetes import client, config
from lib import convert
import warnings
import collections.abc

# Load token or kubeconfig
# Configs can be set in Configuration class directly or using helper utility
warnings.simplefilter("ignore")
try:
    config.load_kube_config()
except FileNotFoundError:
    config.load_incluster_config()

v1 = client.CoreV1Api()


def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.abc.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def get_cluster_capacity():
    cpu_a = 0
    mem_a = 0

    data = {
        "cluster": {
            "allocatable": {}
        },
        "nodes": {}
    }

    ret = v1.list_node()
    for node in ret.items:
        data["nodes"][node.metadata.name] = {
            "cpu": convert.cpu_to_cores(node.status.allocatable["cpu"]),
            "memory": convert.mem_to_bytes(node.status.allocatable["memory"])
        }
        cpu_a += convert.cpu_to_cores(node.status.allocatable["cpu"])
        mem_a += convert.mem_to_bytes(node.status.allocatable["memory"])

    dict_merge(data["cluster"]["allocatable"], {"cpu": cpu_a, "memory": mem_a})
    return data


def get_cluster_resource_quota():
    cpu = 0
    mem = 0

    data = {
        "cluster": {
            "quota": {
                "cpu": "",
                "memory": ""
            }
        },
        "namespaces": {}
    }

    ret = v1.list_resource_quota_for_all_namespaces()
    for quota in ret.items:
        namespace = quota.metadata.namespace
        q_cpu = convert.cpu_to_cores(quota.spec.hard["cpu"])
        q_mem = convert.mem_to_bytes(quota.spec.hard["memory"])

        # Ensure we only count one quota for a namesapce
        if namespace not in data["namespaces"]:
            cpu += q_cpu
            mem += q_mem
            data["namespaces"][namespace] = {
                "quota": {
                    "cpu": q_cpu,
                    "memory": q_mem
                }
            }
            continue

        # There are multiple quotas, let's count the one for non terminating pods
        #  we also need to remember to subtract the value we're replacing from the totals
        if quota.spec.scopes and "NotTerminating" in quota.spec.scopes:
            cpu += q_cpu - data["namespaces"][namespace]["quota"]["cpu"]
            mem += q_mem - data["namespaces"][namespace]["quota"]["memory"]
            dict_merge(data["namespaces"][namespace]["quota"], {
                       "cpu": q_cpu, "memory": q_mem})

    dict_merge(data["cluster"]["quota"], {"cpu": cpu, "memory": mem})
    return data


def get_request_limit_totals():
    ret = v1.list_pod_for_all_namespaces(watch=False)

    mem_requests = 0
    mem_limits = 0
    cpu_requests = 0
    cpu_limits = 0

    data = {
        "cluster": {
            "requests": {
                "cpu": "",
                "memory": "",
            },
            "limits": {
                "cpu": "",
                "memory": "",
            }
        },
        "namespaces": {}
    }

    for pod in ret.items:
        # Ignore pods that aren't running
        if pod.status.phase != "Running":
            continue

        pod_data = {
            pod.metadata.name: {}
        }

        if pod.metadata.namespace not in data["namespaces"]:
            dict_merge(data["namespaces"], {
                pod.metadata.namespace: {
                    "requests": {
                        "cpu": 0,
                        "memory": 0
                    },
                    "limits": {
                        "cpu": 0,
                        "memory": 0
                    }
                }
            })

        ns_data = data["namespaces"][pod.metadata.namespace]

        for c in pod.spec.containers:

            if c.resources is None:
                continue

            c_data = {
                "requests": {},
                "limits": {}
            }

            if c.resources.limits is not None:
                if "cpu" in c.resources.limits:
                    c_cpu = convert.cpu_to_cores(c.resources.limits["cpu"])
                    c_data["limits"]["cpu"] = c_cpu
                    ns_data["limits"]["cpu"] += c_cpu
                    cpu_limits += c_cpu
                if "memory" in c.resources.limits:
                    c_mem = convert.mem_to_bytes(c.resources.limits["memory"])
                    c_data["limits"]["memory"] = c_mem
                    ns_data["limits"]["memory"] += c_mem
                    mem_limits += c_mem
            if c.resources.requests is not None:
                if "cpu" in c.resources.requests:
                    c_cpu = convert.cpu_to_cores(c.resources.requests["cpu"])
                    c_data["requests"]["cpu"] = c_cpu
                    ns_data["requests"]["cpu"] += c_cpu
                    cpu_requests += c_cpu
                if "memory" in c.resources.requests:
                    c_mem = convert.mem_to_bytes(
                        c.resources.requests["memory"])
                    c_data["requests"]["memory"] = c_mem
                    ns_data["requests"]["memory"] += c_mem
                    mem_requests += c_mem

            if c_data:
                dict_merge(pod_data[pod.metadata.name], {c.name: c_data})

        if pod_data:
            dict_merge(data["namespaces"][pod.metadata.namespace], pod_data)

        dict_merge(data["namespaces"][pod.metadata.namespace], ns_data)

    dict_merge(data["cluster"]["requests"], {
        "cpu": cpu_requests, "memory": mem_requests})
    dict_merge(data["cluster"]["limits"], {
               "cpu": cpu_limits, "memory": mem_limits})
    return data


def get_capacity_data():
    capacity = {}
    dict_merge(capacity, get_cluster_capacity())
    dict_merge(capacity, get_cluster_resource_quota())
    dict_merge(capacity, get_request_limit_totals())

    return capacity
