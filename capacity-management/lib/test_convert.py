import convert


def test_cpu():
    cpu = "1000m"
    assert convert.cpu_to_cores(
        cpu) == 1, "{} Should convert to 1 core".format(cpu)


def test_memory_converts():
    memory = "64Mi"
    assert convert.mem_from_bytes(
        convert.mem_to_bytes(memory), "Mi") == 64, "Should be 64"


def test_gb_to_gib():
    gb = "1Gi"
    gib = 0.931323
    assert convert.mem_from_bytes(convert.mem_to_bytes(
        gb), "Gi"), "{} GB Shoould convert to {} GiB.".format(gb, gib)
