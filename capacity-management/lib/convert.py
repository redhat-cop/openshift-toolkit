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
