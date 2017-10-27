Ansible Playbook: Openshift Custom Login Page
=========

This playbook contains Jooho.image-resize and Jooho.openshift_custom_login_page.
It resizes an image to fit for logo accordingly for openshift custom login page. 

Refer this [doc](https://goo.gl/2L45bJ)

Requirements
------------
None

Dependencies
------------

- [Jooho.image-resize](https://galaxy.ansible.com/Jooho/image-resize/)
- [Jooho.openshift-custom-login-page](https://galaxy.ansible.com/Jooho/openshift-custom-login-page/)

Roles Variables
--------------

| Name                      | Default value                         |        Requird       | Description                                                                 |
|---------------------------|---------------------------------------|----------------------|-----------------------------------------------------------------------------|
| openshift_master_conf_dir | /etc/origin/master                    |         no           | Where openshift configuation dir is                                         |
| master_url                | http://master1.example.com:8443       |         no           | API Server URL                                                              |
| login_html_dir            | /etc/origin/master                    |         no           | Where new login html page will locate                                       |
| temp_dir                  | /tmp                                  |         no           | Temp directory                                                              |
| input_img                 | sample-openshift-ori.png              |         no           | Original Image InputPath                                                    |
| output_img_file           | /tmp/sample-openshift-ori.png         |         no           | Resized Image Output and Logo Path                                          |
| size                      | 193x144                               |         no           | Resized Image Size                                                          |
| overwrite_force           | true                                  |         no           | If true, it overwrite exist resized image

**NOTE**
If you want to use different vars from default one, you should specify them with -e options

Example Execute Command
-----------------------

- Download roles
~~~
ansible-galaxy install -f -r requirements.yaml
~~~

- Use default logo
~~~
ansible-playbook ./playbook.yaml -e master_url=lb.example.com:8443
~~~

- Use your own logo
~~~
ansible-playbook ./playbook.yaml -e master_url=lb.example.com:8443 -e input_img=/path/to/logo.png
~~~

After Work
----------
~~~
# Restart Openshift Master Server restart

# Single Master
ansible masters -m shell -a "systemctl restart atomic-openshift-master"

# Multiple Masters
ansible masters -m shell -a "systemctl restart atomic-openshift-master-api"

~~~

License
-------

BSD/MIT

Author Information
------------------

This role was created in 2016 by [Jooho Lee](http://github.com/jooho).

