#!/bin/bash

DOCKER_IMAGE=$1

usage(){
  echo "Usage: etcd_container.service.sh {ETCD_IMAGE}"
  exit 2
}

if [[ "$1" == "" ]];then
  usage
else
  cat > /etc/systemd/system/etcd_container.service <<EOF
  [Unit]
  Description=The Etcd Server container
  After=docker.service
  Requires=docker.service
  PartOf=docker.service

  [Service]
  EnvironmentFile=/etc/etcd/etcd.conf
  ExecStartPre=-/usr/bin/docker rm -f etcd_container
  ExecStart=/usr/bin/docker run --name etcd_container --rm -v /var/lib/etcd:/var/lib/etcd:z -v /etc/etcd:/etc/etcd:z --env-file=/etc/etcd/etcd.conf --net=host --entrypoint=/usr/bin/etcd ${DOCKER_IMAGE}
  ExecStop=/usr/bin/docker stop etcd_container
  SyslogIdentifier=etcd_container
  Restart=always
  RestartSec=5s

  [Install]
  WantedBy=docker.service
EOF
fi
