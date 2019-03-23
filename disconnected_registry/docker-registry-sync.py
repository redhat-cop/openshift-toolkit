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
import re

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
parser.add_argument('--openshift-version', action='store', dest='ocp_version',
                    help='The version of OpenShift which you want to sync images for')

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

# Set the default registry auth file location
docker_auth_config_json = "/root/.docker/config.json"

if options.ocp_version is not None:
    release_version = options.ocp_version

retrieve_v_tags_from_redhat_list = []
retrieve_non_v_tags_from_redhat_list = []

latest_tag_list = []
failed_images = []


# Take first value of api list generated and attempt a GET to see if upstream server challenge us back for auth.
def get_registry_auth_mechanism(url_list):
    auth_session = requests.Session()
    test_api_url = url_list[1]
    logging.debug("Test if authentication mechanism configured for URL: %s" % test_api_url)
    remote_auth_session = auth_session.get(test_api_url)
    remote_auth_resp_code = remote_auth_session.status_code
    if remote_auth_resp_code == 200:
        return False
    elif remote_auth_resp_code == 401:
        # Get header for auth challenge, transform and return back to caller.
        # TODO: parse and normalize header response. redhat.io Apache has 'WWW-' while quay.io nginx using 'www-'.
        auth_challenge_realm = remote_auth_session.headers['WWW-Authenticate']
        # TODO: Fix this ugly re.compile REGEX to transform object into group.
        match = re.compile(r"=(.*)")
        header_match = match.search(auth_challenge_realm)
        challenge_url_join = header_match.group(1).replace('",', "?").replace('"', '')
        challenge_url = challenge_url_join.replace('"', '')
        logging.info("Received www-authenticate challenge at: %s" % challenge_url)
        return challenge_url
    else:
        # TODO: Sometime CDN gateway will return 504: Gateway timeout.
        #  Should do retry for count=x and failed when try=x for better experience"
        print("Upstream registry malfunction when getting %s with HTTP response: %s" % (test_api_url,
                                                                                        remote_auth_resp_code))
        print("Terminating program, please retry again...")
        sys.exit(1)


# Authenticate with docker v2 compatible registry, read from config.json as auth token input,
# authenticate to the challenge server, get access token and return it to the caller.
def get_registry_access_token(registry_name, challenge_url, remote_registry_auth_json_file=None):
    if remote_registry_auth_json_file:
        auth_config_location = remote_registry_auth_json_file
    else:
        from os.path import expanduser
        user_home_dir = expanduser("~")
        auth_config_location = "%s/.docker/config.json" % user_home_dir
    if not auth_config_location:
        print(auth_config_location)
        print("Unable to find and read config.json for authentication. "
              "Did you performed 'docker login' or supply auth file?")
        sys.exit(1)
    else:
        with open(auth_config_location) as auth_data:
            reg_auth_json_data = json.load(auth_data)
        reg_upstream_auth_user_token = reg_auth_json_data['auths'][registry_name]['auth']
    try:
        auth_session = requests.Session()
        auth_header = {'Authorization': 'Basic %s' % reg_upstream_auth_user_token}
        get_auth_token = auth_session.get(challenge_url, headers=auth_header)
        parse_get_resp = json.loads(get_auth_token.text)
        reg_upstream_access_token = parse_get_resp['access_token']
        return reg_upstream_access_token
    except Exception as e:
        return e


def generate_url_list(dictionary_key, list_to_populate, remote_registry):
    for namespace in config_file_dict[dictionary_key]:
        for image in config_file_dict[dictionary_key][namespace]:
            docker_json_link = "https://%s/v2/%s/%s/tags/list" % (remote_registry, namespace, image)
            list_to_populate.append(docker_json_link)


def get_latest_tag_from_api(url_list, tag_list, failed_image_list, version_type=None, registry_access_token=None):
    session = requests.Session()
    for url in url_list:
        logging.info("Processing tags for: %s" % url)
        # If registry_access_token supplied add authorization bearer header to GET request.
        if registry_access_token:
            remote_access_auth_header = {'Authorization': 'Bearer %s' % registry_access_token}
            remote_registry_resp = session.get(url, headers=remote_access_auth_header)
        else:
            remote_registry_resp = session.get(url)
        try:
            # The object is returned as a string so it needs to be converted to a json object
            image_tag_dictionary = json.loads(remote_registry_resp.text)
        except ValueError as e:
            logging.error("ERROR: Unable to parse response from registry")
            logging.error("  URL: %s" % url)
            logging.error("  Response Code: %s" % remote_registry_resp.code)
            logging.error("  Response: %s" % remote_registry_resp.text)
            raise e
        # Get the latest version for a given release
        latest_tag = ''
        image_name = image_tag_dictionary['name']
        for tag in image_tag_dictionary['tags']:
            # check to see if there is a 'v' in the version tag:
            if tag.startswith('v'):
                # Ensures that a valid version is being parsed and searched for
                # release based on a two series release (i.e. 3.9 or 3.10)
                temp_tag = tag.split('.')
                req_tag = ".".join(temp_tag[:2])
            else:
                req_tag = ''
            if release_version in req_tag or not 'openshift' in url:
                # if release_version in tag[:splice_position] or not 'openshift' in url:
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
            logging.error("Unable to match the version for image: %s" % image_name)
            logging.error("Are you sure that the version exists in the RedHat registry?")
            logging.info("Attempting to pull image tag 'latest' instead")
            # insted of failing we will try to pull the tag 'latest'
            # failed_image_list.append(image_name)
            tag_list.append("%s:%s" % (image_name, 'latest'))
        else:
            tag_list.append("%s:%s" % (image_name, latest_tag_minus_hyphon))

        # If package is an rhgs3 package grab the version and 'latest', discovered trying to deploy 3.10 disconnected
        if 'rhgs3/' in image_name:
            tag_list.append("%s:%s" % (image_name, 'latest'))


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
    return exit_with_error


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

generate_url_list('core_components', retrieve_v_tags_from_redhat_list, options.remote_registry)
generate_url_list('hosted_components', retrieve_non_v_tags_from_redhat_list, options.remote_registry)

auth_challenge_url = get_registry_auth_mechanism(retrieve_v_tags_from_redhat_list)

if auth_challenge_url is False:
    logging.info("Registry did not return challenge, continue...")
    get_latest_tag_from_api(retrieve_v_tags_from_redhat_list, latest_tag_list, failed_images,
                            registry_access_token=None)
    get_latest_tag_from_api(retrieve_non_v_tags_from_redhat_list, latest_tag_list, failed_images,
                            registry_access_token=None)
else:
    logging.info("Registry asking for challenge, authenticating (ensure you already run docker login!)...")
    reg_access_token = get_registry_access_token(options.remote_registry, auth_challenge_url,
                                                 remote_registry_auth_json_file=docker_auth_config_json)
    get_latest_tag_from_api(retrieve_v_tags_from_redhat_list, latest_tag_list, failed_images,
                            registry_access_token=reg_access_token)

    get_latest_tag_from_api(retrieve_non_v_tags_from_redhat_list, latest_tag_list, failed_images,
                            registry_access_token=reg_access_token)

total_number_of_images_to_download = len(latest_tag_list)
counter = 1

logging.info("")
logging.info("Total images to download: %s" % total_number_of_images_to_download)

#
# Generate initial array list if local registry is a tar file
#
if options.local_registry == 'tar':
    cmd = ['docker', 'save', '-o', 'ose3-images.tar']

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
    logging.warning("")
    logging.warning("%s/%s failed to download version requested fell back to 'latest': %s"
                    % (number_of_failures, number_of_images_attempted, failed_images))