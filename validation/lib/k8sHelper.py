# Creator: Muhammad Aizuddin Bin Zali < mzali@redhat.com>
# Date Created: 7th April 2019
# Primary Function: k8s helper library for pytest validation.

from kubernetes import client, config


class k8sHelper:
    def __init__(self):
        config.load_kube_config()

        # Make v1 and cv1 as global pointer that can be called from anywhere when this class instantiated.
        global v1
        global cv1
        v1 = client.CoreV1Api()
        cv1 = client.CustomObjectsApi()

    def get_running_pods_by_label(self, namespace, label):
        self.ret = v1.list_namespaced_pod(
            namespace, field_selector='status.phase=Running', label_selector=label)
        return len(self.ret.items)

    def get_route_by_name(self, namespace, name):
        self.routes = cv1.list_namespaced_custom_object('route.openshift.io', 'v1', namespace, 'routes')
        jsonpath_expr = parse('items[?metadata.name == {}].$'.format(name))
        return [match.value for match in jsonpath_expr.find(self.routes)][0]

    def get_node_count(self):
        self.ret = v1.list_node()
        return len(self.ret.items)

    def get_node_by_label(self, label):
        self.ret = v1.list_node(selector=label)
        return self.ret
