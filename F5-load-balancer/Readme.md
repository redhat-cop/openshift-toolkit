# Configuring F5 Big IP for OpenShift

This playbook configures an F5 Load balancer for Openshift Master and Infra-node instances. The playbook creates the monitor, node pools and virtual server (VIP). There is also a configuration example script in case the config is done manually.

The playbook requires `f5-sdk` module which can be installed with `pip3 install f5-sdk`.

The configuration is done on the playbook `vars` section. The connection config is done on the `providers` section:

```yaml
    provider:
      # Setup F5 Big-IP connection parameters
      server: '192.168.1.10'
      user: 'admin'
      password: 'secret'
      ...
```

Each LB instance is configured in a structure like:

```yaml
      {
        name: 'Master-https',
        port: 443,
        monitor: true,
        monitor_type: 'master',
        vip: '192.168.10.100',
        # Add the nodes below using either the hostname OR the IP. Do not add to both.
        node_hostnames: ['openshift-master-1.myorg.com', 'openshift-master-2.myorg.com', 'openshift-master-3.myorg.com'],
        node_ips: ['192.168.100.200']
        },
```

To run the playbook, use the command: `ansible-playbook F5-loadbalancer.yml`.

After running, the instances are created:

![pools](/F5-load-balancer/img/img1.jpeg)
![vip](/F5-load-balancer/img/img2.jpeg)
![monitor](/F5-load-balancer/img/img3.jpeg)

## Manual configuration for Openshift 4

### Master LB (Control Plane)

```bash
create ltm node openshift-master-1.myorg.com fqdn { name openshift-master-1.myorg.com }
create ltm node openshift-master-2.myorg.com fqdn { name openshift-master-2.myorg.com }
create ltm node openshift-master-3.myorg.com fqdn { name openshift-master-3.myorg.com }
create ltm node openshift-bootstrap.myorg.com fqdn { name openshift-bootstrap.myorg.com }
create ltm monitor https ocp-master-mon defaults-from https send "GET /healthz"
create ltm pool master.myorg.com monitor ocp-master-mon members add { openshift-master-1.myorg.com:443 openshift-master-2.myorg.com:443 openshift-master-3.myorg.com.com:443 openshift-bootstrap.myorg.com:443}
create ltm virtual OpenShift-Master pool master.myorg.com source-address-translation { type automap } destination 192.168.10.100:443 profiles add { fastL4 }
create ltm pool master.myorg.com monitor ocp-master-mon members add { openshift-master-1.myorg.com:80 openshift-master-2.myorg.com:80 openshift-master-3.myorg.com.com:80 openshift-bootstrap.myorg.com:80}
create ltm virtual OpenShift-Master pool master.myorg.com source-address-translation { type automap } destination 192.168.10.100:80 profiles add { fastL4 }
create ltm pool master.myorg.com monitor ocp-master-mon members add { openshift-master-1.myorg.com:6443 openshift-master-2.myorg.com:6443 openshift-master-3.myorg.com.com:6443 openshift-bootstrap.myorg.com:6443}
create ltm virtual OpenShift-Master pool master.myorg.com source-address-translation { type automap } destination 192.168.10.100:6443 profiles add { fastL4 }
create ltm pool master.myorg.com monitor ocp-master-mon members add { openshift-master-1.myorg.com:22623 openshift-master-2.myorg.com:22623 openshift-master-3.myorg.com.com:22623 openshift-bootstrap.myorg.com:22623}
create ltm virtual OpenShift-Master pool master.myorg.com source-address-translation { type automap } destination 192.168.10.100:22623 profiles add { fastL4 }
```

Where:

**Master Nodes**: `openshift-master-1.myorg.com, openshift-master-2.myorg.com, openshift-master-3.myorg.com`  
**Bootstrap Node**: `openshift-bootstrap.myorg.com`  
**Pool Name**: `master.myorg.com`  
**Monitor Name**: `ocp-master-mon`  
**Ports**: In this case, masters were configured to use port **443**. In case it's **8443**, update corresponding lines  
**Vip IP**: `192.168.10.100` (Change according to the required VIP VLAN)  

The **bootstrap node** must be removed from the IP Pool after cluster deployment is complete.

### Infra Node / Router LB (One for each Infra pool)

```bash
create ltm node openshift-infranode-1.myorg.com fqdn { name openshift-infranode-1.myorg.com }
create ltm node openshift-infranode-2.myorg.com fqdn { name openshift-infranode-2.myorg.com }
create ltm node openshift-infranode-3.myorg.com fqdn { name openshift-infranode-3.myorg.com }
create ltm monitor http ocp-router defaults-from http send "GET /healthz" destination "*.1936"
create ltm pool infra.myorg.com-http monitor ocp-router members add { openshift-infranode-1.myorg.com:80 openshift-infranode-2.myorg.com:80 openshift-infranode-3.myorg.com:80 }
create ltm pool infra.myorg.com-https monitor ocp-router members add { openshift-infranode-1.myorg.com:443 openshift-infranode-2.myorg.com:443 openshift-infranode-3.myorg.com:443 }
create ltm virtual infra.myorg.com-http  pool infra.myorg.com-http  persist replace-all-with { source_addr } source-address-translation { type automap } destination 192.168.10.101:80 profiles add { fastL4 }
create ltm virtual infra.myorg.com-https pool infra.myorg.com-https persist replace-all-with { source_addr } source-address-translation { type automap } destination 192.168.10.101:443 profiles add { fastL4 }
```

Where:

**Infra Nodes**: `openshift-infranode-1.myorg.com, openshift-infranode-2.myorg.com, openshift-infranode-3.myorg.com`  
**HTTP Pool Name**: `infra.myorg.com-http`  
**HTTPS Pool Name**: `infra.myorg.com-https`  
**Monitor Name**: `ocp-router`  
**VIP IP:** `192.168.10.101` (Change according to the required VIP VLAN)  

## Manual configuration for Openshift 3

### Master LB

```bash
create ltm monitor https ocp-master-mon defaults-from https send "GET /healthz"
create ltm node openshift-master-1.myorg.com fqdn { name openshift-master-1.myorg.com }
create ltm node openshift-master-2.myorg.com fqdn { name openshift-master-2.myorg.com }
create ltm node openshift-master-3.myorg.com fqdn { name openshift-master-3.myorg.com }
create ltm pool master.myorg.com monitor ocp-master-mon members add { openshift-master-1.myorg.com:443 openshift-master-2.myorg.com:443 openshift-master-3.myorg.com.com:443 }
create ltm virtual OpenShift-Master pool master.myorg.com source-address-translation { type automap } destination 192.168.10.100:443 profiles add { fastL4 }
```

Where:

**Master Nodes**: `openshift-master-1.myorg.com, openshift-master-2.myorg.com, openshift-master-3.myorg.com`  
**Pool Name**: `master.myorg.com`  
**Monitor Name**: `ocp-master-mon`  
**Ports**: In this case, masters were configured to use port **443**. In case it's **8443**, update corresponding lines  
**Vip IP**: `192.168.10.100` (Change according to the required VIP VLAN)  

### Infra Node / Router LB (One for each Infra pool)

```bash
create ltm node openshift-infranode-1.myorg.com fqdn { name openshift-infranode-1.myorg.com }
create ltm node openshift-infranode-2.myorg.com fqdn { name openshift-infranode-2.myorg.com }
create ltm node openshift-infranode-3.myorg.com fqdn { name openshift-infranode-3.myorg.com }
create ltm monitor http ocp-router defaults-from http send "GET /healthz" destination "*.1936"
create ltm pool infra.myorg.com-http monitor ocp-router members add { openshift-infranode-1.myorg.com:80 openshift-infranode-2.myorg.com:80 openshift-infranode-3.myorg.com:80 }
create ltm pool infra.myorg.com-https monitor ocp-router members add { openshift-infranode-1.myorg.com:443 openshift-infranode-2.myorg.com:443 openshift-infranode-3.myorg.com:443 }
create ltm virtual infra.myorg.com-http  pool infra.myorg.com-http  persist replace-all-with { source_addr } source-address-translation { type automap } destination 192.168.10.101:80 profiles add { fastL4 }
create ltm virtual infra.myorg.com-https pool infra.myorg.com-https persist replace-all-with { source_addr } source-address-translation { type automap } destination 192.168.10.101:443 profiles add { fastL4 }
```

Where:

**Infra Nodes**: `openshift-infranode-1.myorg.com, openshift-infranode-2.myorg.com, openshift-infranode-3.myorg.com`  
**HTTP Pool Name**: `infra.myorg.com-http`  
**HTTPS Pool Name**: `infra.myorg.com-https`  
**Monitor Name**: `ocp-router`  
**VIP IP:** `192.168.10.101` (Change according to the required VIP VLAN)  