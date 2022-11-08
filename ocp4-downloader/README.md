# OpenShift 4 downloader
## Description
This script will allow you to download some products related with OpenShift 4.

It will create `$HOME/bin` directory if not exists and will download the selected products on it using a naming convention which includes the version, so you will be able to use any version at any time.

It will also use symlinks to choose the downloaded version and will let you manage the symlinks easily.

## Disclaimer
While this script will allow you to download product related with OpenShift 4 from their public locations, please be aware that you'd better review the official documentation of each product. I will do my best in keeping the public URLs updated but if the official documentations refers to another location, you may be out of support if you use this ones.

## Usage
~~~
Usage: ocp4-downloader [--force] [--version <ver>] [--all|--client|--install|installer|--crc|--odo] [--set]
  --all               downloads all products
  --client|--oc       downloads OpenShift CLI (oc / kubectl)
  --crc               downloads CodeReady Containers (crc)
  --force             deletes any existing file matching the version
  --help|-h           shows this message
  --install|installer downloads OpenShift Installer (openshift-install)
  --odo               downloads OpenShift CLI for Developers (odo)
  --set               updates the symlink to whatever set in --version parameter
  --version <ver>     select the version to download for all components. Default: latest
~~~

## Demo
![Examples Overview](resources/overview-ascii.gif)

## Todo
- List existing versions
- Delete existing version

## Contact
Reach me in [Twitter] or email in soukron _at_ gmbros.net

## License
Nothing to be licensed, but just in case, everything in this repo is licensed under GNU GPLv3 license. You can read the document [here].

[Twitter]:http://twitter.com/soukron
[here]:http://gnu.org/licenses/gpl.html

