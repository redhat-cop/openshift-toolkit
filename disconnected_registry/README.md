# Scripts for Executing Disconnected Installs

## Quickstart

1. Install a registry server

  ```bash
  yum install -y docker docker-distribution python-requests firewalld

  systemctl enable firewalld
  systemctl start firewalld

  firewall-cmd --add-port 5000/tcp --permanent
  firewall-cmd --reload

  systemctl enable docker-distribution
  systemctl start docker-distribution
  ```

2. Run the `docker-registry-sync.py` script:
   
   a. To sync Red Hat images to private registry.

  ```
  ./docker-registry-sync.py --from=registry.access.redhat.com --to=<registry-server-ip>:5000 --file=./docker_tags.json
  ```

   b. To sync Red Hat images to ose-images.tar

  ```
  ./docker-registry-sync.py --from=registry.access.redhat.com --to=tar --file=./docker_tags.json
  ```

## Adding Images to Sync List

The set(s) of images that get synced reside in the `docker_tags.json` file. These lists can be added to or edited in order to change the images that get synced.
