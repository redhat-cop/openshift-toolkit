# README

Description:

It was discovered in an OpenShift Cluster deployed into AWS that the AWS NVME disk order changes after reboot in the Red Hat Enterprise Linux 7 operating system. This impacts docker's storage configuration negatively if you have multiple disks configured. This repo contains two basic playbooks that address the two core use cases.

# Use Case 1: Pre Docker Storage Setup

If you are configuring docker storage for the first time:

ocp-aws-nvme-docker-preinstall.yml

# Use Case 2: Post Docker storage setup

If you have already configured docker storage, disks have changed order, and you need to fix dockers configuration in order to bring up the service: 

ocp-aws-nvme-docker-preinstall-fix.yml 
