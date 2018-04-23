FROM jboss-eap-7/jboss-eap70-openshift:1.5
USER root

ENV JAVA_HOME="/usr/lib/jvm/jdk1.8.0" \
    JAVA_VENDOR="Oracle" \
    JAVA_VERSION="1.8.0"

RUN INSTALL_PKGS="java-1.8.0-oracle-devel" && \
    yum install -y $INSTALL_PKGS && \
    yum clean all

USER 185
