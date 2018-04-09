# Tooling for Setting up a Proper Image Management Workflow in OpenShift

The purpose of this project is to be used as a bootstrap for an custom based image build workflow.

## Architecture

The projects here contain the following structures:

- An [OpenShift Applier](https://github.com/redhat-cop/openshift-applier) inventory for the Operator portion of the automation
- An [OpenShift Applier](https://github.com/redhat-cop/openshift-applier) inventory for the Image Builder portion of the automation. _NOTE: Image Builder is a generic term for the actor in the organization who has ownership of Base Image Builds_
- Two sample base image builds
  - [myorg-openjdk18](./myorg-openjdk18) - A sample showing how an org might customize the Red Hat jdk image to insert their corporate CAs
  - [myorg-eap-oraclejdk](./myorg-eap-oraclejdk) - A sample showing an org that has replaced OpenJDK with OracleJDK in the Red Hat image.

The image build workflow has the following stages:

- An `image-management` project
