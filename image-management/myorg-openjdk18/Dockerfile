FROM redhat-openjdk-18/openjdk18-openshift:1.2

USER root

RUN update-ca-trust force-enable
ADD certs/myorg*.pem /etc/pki/ca-trust/source/anchors/

RUN chmod a+r /etc/pki/ca-trust/source/anchors/myorg*.pem; \
    update-ca-trust
