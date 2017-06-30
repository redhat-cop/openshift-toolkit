#!/bin/python

import requests, os, json, sys, time
from subprocess import Popen, PIPE
from requests.packages.urllib3.exceptions import InsecureRequestWarning



token = os.environ['TOKEN']
namespace = os.environ['NAMESPACE']
app_name = os.environ['APP_NAME']
hawkular_hostname = os.environ['HAWKULAR_HOSTNAME']

if 'METRIC_PULL_INTERVAL_SECONDS' in os.environ:
    interval = os.environ['METRIC_PULL_INTERVAL_SECONDS']
else:
    interval = 60

if 'SCALE_UP_THRESHOLD' in os.environ:
    scale_up_threshold = os.environ['SCALE_UP_THRESHOLD']
else:
    scale_up_threshold = .7

if 'CA_CERT' in os.environ:
    ca_cert = os.environ['CA_CERT']
else:
    print "WARNING: Disabling SSL Verification. This should not be done in Production."
    print "To get rid of this message, export CA_CERT=/path/to/ca-certificate"
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    ca_cert = False

metrics_url='https://{}/hawkular/metrics/gauges/data'.format(hawkular_hostname)

def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.metrics_url + '?' + '&'.join('{}={}'.format(k, v) for k, v in req.params.items()),
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
    ))

def get_pods(deployment_config):
    version = Popen(["oc", "-n", "{}".format(namespace), "get", "dc/{}".format(deployment_config), "-o", "jsonpath={ .status.latestVersion }"], stdout=PIPE).stdout.read()

    pods = Popen(["oc", "-n", "{}".format(namespace), "get", "pods", "-l", "deployment={}-{}".format(deployment_config, version), "-o", "jsonpath={ .items[*].metadata.name }"], stdout=PIPE).stdout.read()

    return pods.split()

def get_app_usage(app_name, pods):

    total_usage = 0

    for pod in pods:
        total_usage += get_pod_usage(pod, namespace, token)

    return total_usage

def get_app_limit(app_name, pods):

    total_limit = 0

    for pod in pods:
        total_limit += get_pod_limit(pod, namespace, token)

    return total_limit

def get_pod_usage(pod_name, namespace, token):
    params = {
        'tags': 'descriptor_name:memory/usage,pod_name:{}'.format(pod_name),
        'bucketDuration' : '60000ms',
        'stacked' : 'true',
        'start' : '-1mn'
    }

    headers = {
        'Content-Type' : 'application/json',
        'Hawkular-Tenant': namespace,
        'Authorization' : 'Bearer {}'.format(token)
    }

    req = requests.Request(
        'GET',
        metrics_url,
        params=params,
        headers=headers
        )
    prepared = req.prepare()
    s = requests.Session()
    r = s.send(prepared,
        verify=ca_cert)

#    pretty_print_POST(req)
#    print r.text

    usage=r.json()[0]
    return usage["avg"]

def get_pod_limit(pod_name, namespace, token):
    params = {
        'tags': 'descriptor_name:memory/limit,pod_name:{}'.format(pod_name),
        'bucketDuration' : '60000ms',
        'stacked' : 'true',
        'start' : '-1mn'
    }

    headers = {
        'Content-Type' : 'application/json',
        'Hawkular-Tenant': namespace,
        'Authorization' : 'Bearer {}'.format(token)
    }

    req = requests.Request(
        'GET',
        metrics_url,
        params=params,
        headers=headers
        )
    prepared = req.prepare()
    s = requests.Session()
    r = s.send(prepared,
        verify=ca_cert)

#    pretty_print_POST(req)
#    print r.text

    usage=r.json()[0]
    return usage["avg"]

def scale_up(app_name, pod_count):
    print Popen(["oc", "scale", "--replicas={}".format(pod_count+1), "dc/{}".format(app_name)], stdout=PIPE).stdout.read()

while True:
    current_pods = get_pods(app_name)

    usage = get_app_usage(app_name, current_pods)
    limit = get_app_limit(app_name, current_pods)
    if limit <= 0:
        print "ERROR: Cannot scale on apps with no limit defined. Program will exit."
        sys.exit(1)

    print "Average usage is {}".format(usage)
    print "Averate limit is {}".format(limit)
    if usage / limit > scale_up_threshold:
        print "scaling up!"
        scale_up(app_name, len(current_pods))
    else:
        print "staying put"
    print ""
    time.sleep(interval)
