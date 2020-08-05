Role Name
=========

Backup etcd v3 data and config, of static Pods.

Refererence doc: https://docs.openshift.com/container-platform/3.10/day_two_guide/environment_backup.html#etcd-backup_environment-backup

Documentation notes on restoring etcd:

```
The etcdctl backup command rewrites some of the metadata contained in
the backup,specifically, the node ID and cluster ID, which means that in
the backup,the node loses its former identity. To recreate a cluster from
the backup, you create a new, single-node cluster, then add the rest of
the nodes to the cluster. The metadata is rewritten to prevent
the new node from joining an existing cluster.
```

Requirements
------------


Role Variables
--------------


Dependencies
------------


Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
