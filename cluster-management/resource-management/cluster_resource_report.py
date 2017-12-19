#!/usr/bin/env python
import os, json
import requests
from tempfile import NamedTemporaryFile
import socket
 
# Primary Function: This script is designed to log into an OpenShift cluster, read the kube config
# and then retrieve the resources that each pod requests. It produces summed output based on each
# host
# Date: Nov 8, 2017
 
 
def query_cluster_api(master_fqdn):
    """
    :param master_fqdn: the only parameter is the master fqdn, or the openshift master public hostname
    :return: returns a list of "strings" which are actually json objects to be processed by json.loads()
    """
    response_list = []
    # The certificate section below could be done with the python requests module, but since we are
    # exceuting shell commands through a remote host, it is set up to use the 'curl' command
    kube_config_location = "/root/.kube/config"
    client_cert_list_compre = '[word.split(": ")[1].strip() for word in open("%s").readlines() ' \
                              'if "client-certificate-data" in word]' % kube_config_location
    client_key_list_compre = '[word.split(": ")[1].strip() for word in open("%s").readlines() ' \
                             'if "client-key-data" in word]' % kube_config_location
 
    client_cert_base64 = os.popen("sudo python -c 'print %s'" % client_cert_list_compre).read()
    client_cert_decoded = client_cert_base64.strip().strip("[").strip("]").strip("'").decode('base64')
 
    client_key_base64 = os.popen("sudo python -c 'print %s'" % client_key_list_compre).read()
    client_key_decoded = client_key_base64.strip().strip("[").strip("]").strip("'").decode('base64')
 
    pod_url = "https://%s:8443/api/v1/pods" % master_fqdn
    with NamedTemporaryFile(delete=False) as client_file:
      client_file.write(client_cert_decoded)
      client_file.flush()
 
    with NamedTemporaryFile(delete=False) as key_file:
      key_file.write(client_key_decoded)
      key_file.flush()
 
    cert = (client_file.name, key_file.name)
    pod_request = requests.get(pod_url, cert=cert, verify=False)
    return(pod_request)
 
 
def process_json_response(dictionary, json_response, resource_type):
    """
 
    :param dictionary: usually a blank dictionary which is updated with specific data from the json response
    :param json_response: a json formatted response received from the OpenShift API
    :param resource_type: expected values are either 'limits' or 'requests'
    :return: nothing. This function updates the dictionaries passed in.
    """
    pod_counter = 0
    # The dictionary has the following structure:
    # { <node>: {<pod_name>: {<container_name> {<memory_request>: <value>, <cpu_request>: <value>} }}}
    # each pod will have multiple containers in it
    pod_name = json_response['metadata']['name']
    node_name = json_response['spec']['nodeName']
    container_count = 0
    while container_count != len(json_response['spec']['containers']):
        container_name = json_response['spec']['containers'][container_count]['name']
        try:
            # This if block makes sure to update the appropriate section of the dictionary if data is already
            # present.
            if node_name in dictionary:
                if pod_name in dictionary[node_name]:
                    dictionary[node_name][pod_name].update({container_name: {'memory': json_response['spec']
                                                          ['containers'][container_count]['resources']
                                                          [resource_type]['memory'],
                                                          'cpu': json_response['spec']['containers']
                                                            [container_count]['resources'][resource_type]['cpu']}})
                else:
                    dictionary[node_name].update({pod_name: {container_name: {'memory': json_response['spec']
                                                            ['containers'][container_count]['resources']
                                                            [resource_type]['memory'],
                                                            'cpu': json_response['spec']['containers']
                                                            [container_count]['resources'][resource_type]['cpu']}}})
            else:
                dictionary.update({node_name: {pod_name: {container_name: {'memory': json_response
                                  ['spec']['containers'][container_count]['resources'][resource_type]['memory'],
                                  'cpu': json_response['spec']['containers'][container_count]
                                  ['resources'][resource_type]['cpu']}}}})
        except:
            pass
        container_count += 1
 
 
 
def convert_units(process_this_dict, total_resources_dict, resource_type):
    """
 
    :param process_this_dict: dictionary which has raw data in it in the form of  {node_name: {pod_name:
          {container_name: {'memory': '3G', 'cpu': '100m'}}}}
    :param total_resources_dict: An dictionary to hold all of the units of measurement which were converted to the
           lowest unit (i.e. Mi instead of Gi, or milicores instead of full cores)
    :param resource_type: has a value of either 'limits' or 'requests'
    :return: nothing. Adds converted data to the total_resources_dict which is passed in
    """
    # For now the script only converts between Megs and Gigs. Test cluster did not have other
    # units of measurement.
 
    for node in process_this_dict:
        total_m_cpu = 0
        total_ram_megs = 0
        total_ram_gigs = 0
        for pod in process_this_dict[node]:
            for container in process_this_dict[node][pod]:
                for key, value in process_this_dict[node][pod][container].iteritems():
                    if 'cpu' in key:
                        if 'm' in value:
                            cpu_amount = int(value.split('m')[0])
                            total_m_cpu += cpu_amount
                        else:
                            try:
                                # The assumption is that if milicores are not specified the value is a full CPU
                                # so convert everything to milicores
                                cpu_amount = int(value) * 1000
                                total_m_cpu += cpu_amount
                            except:
                                print("%s did not appear to be specified in milicores or whole numbers" % value)
                    # Units of measurement are unpredictable so assume that both Megabyte (M) and Mebibyte (Mi) are
                    # the same. This is not meant to be an exact measurement but a rough estimate.
                    # The same assumption is made for (G) and (Gi)
                    if 'memory' in key:
                        if 'M' in value:
                            ram_in_megs = int(value.split('M')[0])
                            total_ram_megs += ram_in_megs
                        elif "G" in value:
                            ram_in_gigs = int(value.split('G')[0])
                            total_ram_gigs += ram_in_gigs
                        else:
                            print("%s is not specified with either M, Mi, Gi or G... skipping" % value)
        total_ram_megs += total_ram_gigs * 1024
        if node in total_resources_dict:
            total_resources_dict[node].update({'cpu_%s' % resource_type: total_m_cpu,
                                               'ram_%s' % resource_type: total_ram_megs})
        else:
            total_resources_dict.update({node: {'cpu_%s' % resource_type: total_m_cpu,
                                               'ram_%s' % resource_type: total_ram_megs}})
 
 
def print_report(dictionary):
    """
    :param dictionary: a dictionary that has both requests and limits totals
    :return: Nothing. This function simply prints the contents of a dictionary
    """
    import collections
    # Using an ordered dict so that the cluster type is sorted. There is a slight formatting problem
    # because the node numbers are not sorted properly (i.e. node2 and node20 are displayed after each other)
    ordered_dict = collections.OrderedDict(sorted(dictionary.items()))
    resource_type_list = [{'cpu_requests': 'CPU requests in millicores'}, {'ram_requests': 'Ram requests in megabytes'},
                          {'cpu_limits': 'CPU limits in millicores'}, {'ram_limits': 'Ram limits in megabytes'}]
    for node in ordered_dict:
        print(node)
        for resource in resource_type_list:
            for key, value in resource.iteritems():
                try:
                    print("\t%s: %s" % (value, dictionary[node][key]))
                except:
                    print("\t%s: NOT DEFINED" % value)
 
 
if __name__ == "__main__":
    output_list = query_cluster_api(socket.getfqdn())
 
    requests_dict = {}
    limits_dict = {}
    total_resources_dict = {}
    for result in output_list.json()['items']:
      process_json_response(requests_dict, result, 'requests')
      process_json_response(limits_dict, result, 'limits')
      convert_units(requests_dict, total_resources_dict, 'requests')
      convert_units(limits_dict, total_resources_dict, 'limits')
    print("\n-------------------------------------------------")
    print_report(total_resources_dict)
