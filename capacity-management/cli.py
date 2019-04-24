#!/usr/bin/env python3
import argparse
import json
from lib import capacity, convert


def do_print(capacity):
    cluster_memory = capacity["cluster"]["totals"]["memory"]
    cluster_cpu = capacity["cluster"]["totals"]["cpu"]
    quota_memory = capacity["quota"]["memory"]
    quota_cpu = capacity["quota"]["cpu"]
    total_cpu_requests = capacity["requests"]["totals"]["cpu"]
    total_cpu_limits = capacity["limits"]["totals"]["cpu"]
    total_mem_requests = capacity["requests"]["totals"]["memory"]
    total_mem_limits = capacity["limits"]["totals"]["memory"]
    memory_unit = 'Gi'

    print()
    print('Total Cluster Size:')
    print('----')
    print('\tMemory:\t{} {}'.format(convert.mem_from_bytes(
        cluster_memory, memory_unit), memory_unit))
    print('\tCPU:\t{} Cores'.format(cluster_cpu))
    print()
    print('Amount Claimed By Quota:')
    print('----')
    print(
        '\tMemory:\t{} {} ({}%)'.format(
            convert.mem_from_bytes(
                quota_memory,
                memory_unit
            ),
            memory_unit,
            quota_memory /
            cluster_memory*100
        )
    )
    print(
        '\tCPU:\t{} Cores ({}%)'.format(
            quota_cpu,
            quota_cpu /
            cluster_cpu*100
        )
    )
    print()
    print('Total Limits:')
    print('----')
    print(
        '\tMemory:\t{} {} ({}%)'.format(
            convert.mem_from_bytes(
                total_mem_limits,
                memory_unit
            ),
            memory_unit,
            total_mem_limits/cluster_memory*100
        )
    )
    print('\tCPU:\t{} Cores ({}%)'.format(
        total_cpu_limits, total_cpu_limits/cluster_cpu*100))
    print()
    print('Total Requests:')
    print('----')
    print('\tMemory:\t{} {} ({}%)'.format(convert.mem_from_bytes(
        total_mem_requests, memory_unit), memory_unit, total_mem_requests/cluster_memory*100))
    print('\tCPU:\t{} Cores ({}%)'.format(
        total_cpu_requests, total_cpu_requests/cluster_cpu*100))


parser = argparse.ArgumentParser(description='Report on OpenShift Usage.')
parser.add_argument('-o', '--output', default='console')
args = parser.parse_args()

capacity = capacity.get_capacity_data()
#filename = os.getcwd() + "/tmp/capacity.json"
#with open(filename, 'w+') as f:
#    json.dump(capacity, f)

if args.output == 'console':
    do_print(capacity)
elif args.output == 'json':
    print(json.dumps(capacity, indent=2))
else:
    print("Output format {} not recognized.".format(args.output))
