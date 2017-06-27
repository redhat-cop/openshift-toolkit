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

Jooho.image-resize
Jooho.openshift_custom_webconsole_logo.

Roles Variables
--------------

| Name                      | Default value                         |        Requird       | Description                                                                 |
|---------------------------|---------------------------------------|----------------------|-----------------------------------------------------------------------------|
| openshift_master_conf_dir | /etc/origin/master                    |         yes          | Where openshift configuation dir is                                         |
| master_url                | http://master1.example.com:8443       |         yes          | API Server URL                                                              |
| stylesheet_base_dir       | /etc/origin/master/stylesheet         |         yes          | Where new login html page will locate                                       |
| temp_dir                  | /tmp                                  |         no           | Temp directory                                                              |
| input_img                 | sample-openshift-ori.png              |         yes          | Original Image InputPath                                                    |
| output_img_file           | /tmp/logo.png                         |         yes          | Resized Image Output/Logo Path                                              |
| size                      | 193x144                               |         yes          | Resized Image Size                                                          |
| force                     | false                                 |         no           | If true, it overwrite exist resized image/css                               |


**TIP**
If you want to overwrite variables, updating group_vars/all file is the easest way.


Example group_vars
------------------
```
output_img_file: /path/to/logo.png
```


Example Execute Command
-----------------------
~~~
ansible-galaxy install -r requirements.yaml
ansible-playbook  ./playbook.yaml  --extra-vars output_img_file=/path/to/logo.png
~~~

Example Playbook
----------------
~~~
- name: Example Playbook
  hosts: masters
  gather_facts: false
  pre_tasks:
    - name: Shared values in roles
      set_fact:
         output_img_file: /path/to/logo.png
 
  roles:
     - { role: resize_image, output_img: "{{output_img_file}}", force: true, when: "{{inventory_hostname == groups.masters[0]}}"}
     - { role: configure_login_logo, logo_img: "{{output_img_file}}", master_url: "master1.example.com:8443", stylesheet_base_dir: "/etc/origin/master/stylesheet", force: true }

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

This role was created in 2017 by [Jooho Lee](http://github.com/jooho).

