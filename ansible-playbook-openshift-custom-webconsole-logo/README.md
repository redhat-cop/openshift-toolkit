Ansible Playbook: Openshift Custom Webconsole Logo
=========

This playbook contains Jooho.image-resize and Jooho.openshift_custom_webconsole_logo.
It resizes an image to fit for logo accordingly for openshift custom webconsole logo. 

Refer this [doc](https://goo.gl/2L45bJ)

Requirements
------------
None

Dependencies
------------

- [Jooho.image-resize](https://galaxy.ansible.com/Jooho/image-resize)
- [Jooho.openshift-custom-webconsole-logo](https://galaxy.ansible.com/Jooho/openshift-custom-webconsole-logo)

Roles Variables
--------------

| Name                      | Default value                         |        Requird       | Description                                                                 |
|---------------------------|---------------------------------------|----------------------|-----------------------------------------------------------------------------|
| openshift_master_conf_dir | /etc/origin/master                    |         no           | Where openshift configuation dir is                                         |
| master_url                | http://master1.example.com:8443       |         no           | API Server URL                                                              |
| stylesheet_base_dir       | /etc/origin/master/stylesheet         |         no           | Where new login html page will locate                                       |
| temp_dir                  | /tmp                                  |         no           | Temp directory                                                              |
| input_img                 | sample-openshift-ori.png              |         no           | Original Image InputPath                                                    |
| size                      | 193x144                               |         no           | Resized Image Size                                                          |
| force                     | true                                  |         no           | If true, it overwrite exist resized image/css                               |

**NOTE**
If you want to use different vars from default one, you should specify them with -e options


Example Execute Commands
-----------------------
- **Download roles**
~~~
cd openshift-toolkit/ansible-playbook-openshift-custom-webconsole-logo

ansible-galaxy install -f -r requirements.yaml -p ./roles
~~~

- **Use default logo**

*Options:*
  - If you want to restart master manually, please add `-e restart_master=false`
  - If you want to use your own image, please add `-e input_img=/path/to/logo.png`

~~~
ansible-playbook -i /path/to/hosts ./playbook.yaml 
~~~

- **Use your own logo**
~~~
ansible-playbook -i /path/to/hosts ./playbook.yaml -e input_img=/path/to/logo.png
~~~


Quick Demo Script
----------------
```
git clone https://github.com/redhat-cop/openshift-toolkit.git

cd openshift-toolkit/ansible-playbook-openshift-custom-login-logo

ansible-galaxy install -f -r requirements.yaml -p ./roles

wget https://i.ytimg.com/vi/iai4v0ocX3w/maxresdefault.jpg -O ./superman.jpg

ansible-playbook -i ./hosts ./playbook.yaml -e input_img=./superman.jpg

```

Sample Hosts file
------------------

```
[masters]
master1.example.com

[etcd]
master1.example.com

[nodes]
master1.example.com openshift_node_labels="{'region': 'mgmt', 'role': 'master'}"
node1.example.com   openshift_node_labels="{'region': 'infra', 'role': 'app', 'zone': 'default'}"
node2.example.com   openshift_node_labels="{'region': 'infra', 'role': 'app', 'zone': 'default'}"
```

Movie Clips
-----------
[![asciicast](https://asciinema.org/a/144980.png)](https://asciinema.org/a/144980)

Result Image
------------
![alt Result](./result.png)

License
-------

BSD/MIT

Author Information
------------------

This role was created in 2017 by [Jooho Lee](http://github.com/jooho).

