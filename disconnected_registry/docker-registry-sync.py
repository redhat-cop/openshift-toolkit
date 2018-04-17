#!/usr/bin/python
import requests
import json
from pkg_resources import parse_version
import argparse
import os
import subprocess
import logging
import datetime
import time
import sys

parser = argparse.ArgumentParser(description='Syncs images from a public docker registry to a private registry. Use '
                                             'this to populate private registries in a closed off environment. Must be '
                                             'run from a linux host capable of running docker commands which has '
                                             'access both to the internet and the private registry.',
                                             epilog='%s \nSample usage: --from=<public-registry-hostname> '
                                             '--to=<registry-to-sync-to> --file=<image-file>',
                                             formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--from', action='store', dest='remote_registry', help='The location of the remote repository',
                    required=True)
parser.add_argument('--to', action='store', dest='local_registry', help='The location of the local repository',
                    required=True)
parser.add_argument('--file', action='store', dest='json_file', help='A JSON formatted file with the following format:'
                                                                     '{"<tag_type>": {"<namespace>": ["image1", image2"'
                                                                     'image3]}}', required=True)
parser.add_argument('--dry-run', action='store_true', dest='dry_run', help='If this flag is present, commands will be'
                                                                         'dumped to stdout instead of run')
parser.add_argument('--openshift-version', action='store', dest='ocp_version', help='The version of OpenShift which you '
                                                                              'want to sync images for')

options = parser.parse_args()


# Set up the logger
todays_date = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d--%H_%M'))

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/tmp/docker_registry_%s.log' % todays_date,
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Set the default release version incase unspecified
release_version = '3.7'

if options.ocp_version is not None:
    release_version = options.ocp_version

retrieve_v_tags_from_redhat_list = []
retrieve_non_v_tags_from_redhat_list = []

latest_tag_list = []
failed_images = []


def generate_url_list(dictionary_key, list_to_populate):
    for namespace in config_file_dict[dictionary_key]:
        for image in config_file_dict[dictionary_key][namespace]:
            docker_json_link = "https://registry.access.redhat.com/v2/%s/%s/tags/list" % (namespace, image)
            list_to_populate.append(docker_json_link)


def get_latest_tag_from_api(url_list, tag_list, failed_image_list, version_type = None):
    session = requests.Session()
    for url in url_list:
        redhat_registry = session.get(url)
        try:
            # The object is returned as a string so it needs to be converted to a json object
            image_tag_dictionary = json.loads(redhat_registry.text)
        except ValueError as e:
            logging.error("ERROR: Unable to parse response from registry")
            logging.error("  URL: %s" % url)
            logging.error("  Response Code: %s" % redhat_registry.code)
            logging.error("  Response: %s" % redhat_registry.text)
            sys.exit()
        # Get the latest version for a given release
        latest_tag = ''
        image_name = image_tag_dictionary['name']
        for tag in image_tag_dictionary['tags']:
            # check to see if there is a 'v' in the version tag:
            if tag.startswith('v'):
                # This tracks the position of the splice. It assumes that you are trying to get the latest
                # release based on a two digit release (i.e. 3.4 or 3.7)
                splice_position = 4
            else:
                splice_position = 3
            if release_version in tag[:splice_position] or not 'openshift' in url:
                # There may be a better way of getting the highest tag for a release
                # but the list may potentially have a higher release version than what you are looking for
                if parse_version(tag) > parse_version(latest_tag):
                    if version_type is not None:
                        if "v" in tag:
                            pass
                        else:
                            latest_tag = tag
                    else:
                        latest_tag = tag
        # We want to remove everything after the hyphen because we don't care about release versions
        latest_tag_minus_hyphon = latest_tag.split('-')[0]
        # If the tag has successfully removed a hyphen, it will be unicode, otherwise it will be a string
        if type(latest_tag_minus_hyphon) is not unicode:
            logging.error("Unable to properly parse the version for image: %s" % image_name)
            logging.error("Are you sure that the version exists in the RedHat registry?")
            failed_image_list.append(image_name)
        else:
            tag_list.append("%s:%s" % (image_name, latest_tag_minus_hyphon))


def generate_realtime_output(cmd):
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.STDOUT)
    for stdout_line in iter(output.stdout.readline, ""):
        yield stdout_line.strip()
    output.stdout.close()
    return_code = output.wait()
    if return_code:
        logging.error("There appears to be a problem contacting %s" % cmd[2])
        logging.error("Skipping...")
        yield False
        return


def dry_run_print_docker_commands(remote_registry, local_registry, image_name):
    print("docker pull %s/%s" % (remote_registry, image_name))
    print("docker tag %s/%s %s/%s" % (remote_registry, image_name, local_registry, image_name))
    print("docker push %s/%s" % (local_registry, image_name))
    print("")


def pull_images(remote_registry, image_name):
    logging.info("Pulling %s/%s" % (remote_registry, image_name.strip()))
    exit_with_error = False
    for pulled_image in generate_realtime_output(["docker", "pull", "%s/%s" % (remote_registry,
                                                                               image_name)]):
        if pulled_image:
            logging.info(pulled_image),
        else:
            exit_with_error = True
            break
    return(exit_with_error)


def tag_images(remote_registry, local_registry, image_name):
    os.popen("docker tag %s/%s %s/%s" % (remote_registry, image_name, local_registry,
                                         image_name)).read()


def push_images(local_registry, image_name):
    for pushed_image in generate_realtime_output(["docker", "push", "%s/%s" % (local_registry,
                                                                               image_name)]):
        logging.info(pushed_image),

config_file = options.json_file
with open(config_file) as json_data:
    config_file_dict = json.load(json_data)

generate_url_list('core_components', retrieve_v_tags_from_redhat_list)
generate_url_list('hosted_components', retrieve_non_v_tags_from_redhat_list)

get_latest_tag_from_api(retrieve_v_tags_from_redhat_list, latest_tag_list, failed_images)
get_latest_tag_from_api(retrieve_non_v_tags_from_redhat_list, latest_tag_list, failed_images, 'v')

total_number_of_images_to_download = len(latest_tag_list)
counter = 1

logging.info("")
logging.info("Total images to download: %s" % total_number_of_images_to_download)

#
# Generate initial array list if local registry is a tar file
#
if options.local_registry == 'tar':
    cmd = ['docker','save','-o', 'ose3-images.tar']

for namespace_and_image in latest_tag_list:
    if options.dry_run:
        logging.info("Dry run mode activated. Docker commands were outputted to the screen")
        dry_run_print_docker_commands(options.remote_registry, options.local_registry, namespace_and_image)
    elif options.local_registry == 'tar':
        # create export images for a tar
        if not pull_images(options.remote_registry, namespace_and_image):
           cmd.append(options.remote_registry + '/' + namespace_and_image)
    else:
        logging.info("")
        logging.info("Downloading image %s/%s" % (counter, total_number_of_images_to_download))
        counter += 1
        # If the image pull fails skip the tagging and pushing steps
        if not pull_images(options.remote_registry, namespace_and_image):
            logging.info("Tagging for this registry: %s" % options.local_registry)
            tag_images(options.remote_registry, options.local_registry, namespace_and_image)
            logging.info("Pushing into the local registry...")
            push_images(options.local_registry, namespace_and_image)

##
# create tar file of images
#
if options.local_registry == 'tar':
    for output in generate_realtime_output(cmd):
        logging.info(output),

if failed_images:
    number_of_failures = len(failed_images)
    number_of_images_attempted = total_number_of_images_to_download + number_of_failures
    logging.warn("")
    logging.warn("%s/%s failed to download: %s" % (number_of_failures, number_of_images_attempted, failed_images))
