#!/bin/bash

ORG_ID=1
PRODUCT_NAME="OCP Docker images"

upstream_repos=( openshift3/ose-deployer \ 
     openshift3/ose-docker-registry \
     openshift3/registry-console \
     openshift3/ose-pod \
     openshift3/ose-docker-builder \ 
     openshift3/ose-sti-builder \ 
     openshift3/ose-haproxy-router \ 
     openshift3/logging-elasticsearch \
     openshift3/logging-kibana \
     openshift3/logging-fluentd \
     openshift3/logging-auth-proxy \
     openshift3/metrics-hawkular-metrics \
     openshift3/metrics-cassandra \
     openshift3/metrics-heapster \
     openshift3/ose \
     openshift3/node \
     openshift3/openvswitch \
     rhel7/etcd \
     openshift3/ose-keepalived-ipfailover
)

xpaas_images=( redhat-openjdk-18/openjdk18-openshift \
               jboss-webserver-3/webserver30-tomcat8-openshift \
               jboss-eap-7/eap70-openshift \
               redhat-sso-7/sso70-openshift \
               rhscl/postgresql-95-rhel7 \
               rhscl/nodejs-4-rhel7 \
               rhscl/nodejs-6-rhel7 \
               rhscl/python-27-rhel7 \
               rhscl/python-35-rhel7
)

jenkins_images=( openshift3/jenkins-2-rhel7 \
                 openshift3/jenkins-slave-base-rhel7 \
                 openshift3/jenkins-slave-maven-rhel7 \
                 openshift3/jenkins-slave-nodejs-rhel7
)

hammer product create --name "$PRODUCT_NAME" --organization-id $ORG_ID

for i in ${upstream_repos[@]}; do
  hammer repository create --name "$i" --organization-id $ORG_ID --content-type docker --url "https://registry.access.redhat.com" --docker-upstream-name "$i" --product "$PRODUCT_NAME"
done


for i in ${xpaas_images[@]}; do
  hammer repository create --name "$i" --organization-id $ORG_ID --content-type docker --url "https://registry.access.redhat.com" --docker-upstream-name "$i" --product "$PRODUCT_NAME"
done

for i in ${jenkins_images[@]}; do
  hammer repository create --name "$i" --organization-id $ORG_ID --content-type docker --url "https://registry.access.redhat.com" --docker-upstream-name "$i" --product "$PRODUCT_NAME"
done
