import argparse
import paramiko
import subprocess
import sys
import os
import time

# DEFAULT FILE PATHS
HOURS = 'hours'
MINUTES = 'minutes'
SECONDS = 'seconds'

INVENTORY_PATH = '/vagrant/inventories/development/'
SITE_PATH = '/vagrant/playbook/'

HOST_KEY = 'host'
INVENTORY_FILE_KEY = 'inventory'
SITE_FILE_KEY = 'site'
FULL_PATH_KEY = 'full_path'
TAGS_KEY = 'tags'
MESSAGE_KEY = 'message'
PHONE_NUMBER_KEY = 'phone_number'
DISABLE_ALERT_KEY = 'disable_alert'
STDOUT_KEY = 'stdout'
STDERR_KEY = 'stderr'
SUDO_KEY = 'sudo'
VAGRANT_CWD_KEY = 'vagrant_cwd'
AUDIO_KEY = 'audio_alert'

DEFAULT_HOST = 'controller-01'
DEFAULT_INVENTORY_FILE = 'development'
DEFAULT_SITE_FILE = 'site.yml'
DEFAULT_PHONE_NUMBER = '2147635274'
DEFAULT_MESSAGE = 'Ansible Deployment Complete'

SHORT = 'short'
LONG = 'long'
HELP = 'help'
ACTION = 'action'
ARG_NAME = 'arg_name'
REQUIRED = 'required'
DEFAULT = 'default'

OPTION_HELP = {
    HOST_KEY: 'Host of node to deploy from (default: ' + str(DEFAULT_HOST) + ')',
    INVENTORY_FILE_KEY: 'Inventory file to use for ansible (default: ' + str(DEFAULT_INVENTORY_FILE) + ')',
    SITE_FILE_KEY: 'Site file to use for ansible (default: ' + str(DEFAULT_SITE_FILE) + ')',
    FULL_PATH_KEY: 'Specify inventory/site file with full path\nEX: -f inventory=<full_path_to_inventory_file>,site=<full_path_to_site.yml>',
    TAGS_KEY: 'Ansible tags to run specific roles',
    MESSAGE_KEY: 'Alert message to be sent',
    PHONE_NUMBER_KEY: 'Phone number to alert (default: ' + str(DEFAULT_PHONE_NUMBER) + ')',
    DISABLE_ALERT_KEY: 'Disable the alert when complete',
    STDOUT_KEY: 'Print the stdout from deployment',
    STDERR_KEY: 'Print the stderr from deployment',
    SUDO_KEY: 'Run ansible using sudo',
    VAGRANT_CWD_KEY: 'Path to the directory containing your Vagrantfile (if it\'s not in the current directory)',
    AUDIO_KEY: 'Announce when complete with a message'
}

PROG_DESC = 'Deploy ansible and alert when complete'
ALERT_MSG = 'message={} | EXIT_STATUS: {} | EXEC TIME: {}'

OPTS = {
         HOST_KEY: {
            SHORT: '-H',
            LONG: '--host',
            HELP: OPTION_HELP[HOST_KEY],
            ACTION: None,
            ARG_NAME: 'host',
            REQUIRED: False,
            DEFAULT: DEFAULT_HOST
         },
         INVENTORY_FILE_KEY: {
            SHORT: '-i',
            LONG: '--inventory-file',
            HELP: OPTION_HELP[INVENTORY_FILE_KEY],
            ACTION: None,
            ARG_NAME: 'inventory_file',
            REQUIRED: True,
            DEFAULT: None
         },
         SITE_FILE_KEY: {
            SHORT: '-s',
            LONG: '--site-file',
            HELP: OPTION_HELP[SITE_FILE_KEY],
            ACTION: None,
            ARG_NAME: 'site_file',
            REQUIRED: False,
            DEFAULT: DEFAULT_SITE_FILE
         },
         FULL_PATH_KEY: {
            SHORT: '-f',
            LONG: '--full-path',
            HELP: OPTION_HELP[FULL_PATH_KEY],
            ACTION: None,
            ARG_NAME: 'full_path',
            REQUIRED: False,
            DEFAULT: None
         },
         TAGS_KEY: {
            SHORT: '-t',
            LONG: '--tags',
            HELP: OPTION_HELP[TAGS_KEY],
            ACTION: None,
            ARG_NAME: 'tags',
            REQUIRED: False,
            DEFAULT: None
         },
         SUDO_KEY: {
            SHORT: '-S',
            LONG: '--sudo',
            HELP: OPTION_HELP[SUDO_KEY],
            ACTION: 'store_true',
            ARG_NAME: 'sudo',
            REQUIRED: False,
            DEFAULT: None
         },
         AUDIO_KEY: {
            SHORT: '-a',
            LONG: '--audio_alert',
            HELP: OPTION_HELP[AUDIO_KEY],
            ACTION: 'store_true',
            ARG_NAME: 'audio_alert',
            REQUIRED: False,
            DEFAULT: None
         },
         MESSAGE_KEY: {
            SHORT: '-m',
            LONG: '--alert-message',
            HELP: OPTION_HELP[MESSAGE_KEY],
            ACTION: None,
            ARG_NAME: 'alert_message',
            REQUIRED: False,
            DEFAULT: DEFAULT_MESSAGE
         },
         PHONE_NUMBER_KEY: {
            SHORT: '-p',
            LONG: '--phone-number',
            HELP: OPTION_HELP[PHONE_NUMBER_KEY],
            ACTION: None,
            ARG_NAME: 'phone_number',
            REQUIRED: False,
            DEFAULT: DEFAULT_PHONE_NUMBER
         },
         DISABLE_ALERT_KEY: {
            SHORT: '-d',
            LONG: '--disable-alert',
            HELP: OPTION_HELP[DISABLE_ALERT_KEY],
            ACTION: 'store_true',
            ARG_NAME: 'disable_alert',
            REQUIRED: False,
            DEFAULT: None
         },
         STDOUT_KEY: {
            SHORT: '-o',
            LONG: '--stdout',
            HELP: OPTION_HELP[STDOUT_KEY],
            ACTION: 'store_true',
            ARG_NAME: 'stdout',
            REQUIRED: False,
            DEFAULT: None
         },
         STDERR_KEY: {
            SHORT: '-e',
            LONG: '--stderr',
            HELP: OPTION_HELP[STDERR_KEY],
            ACTION: 'store_true',
            ARG_NAME: 'stderr',
            REQUIRED: False,
            DEFAULT: None
         },
         VAGRANT_CWD_KEY: {
            SHORT: '-V',
            LONG: '--vagrant-cwd',
            HELP: OPTION_HELP[VAGRANT_CWD_KEY],
            ACTION: None,
            ARG_NAME: 'vagrant_cwd',
            REQUIRED: False,
            DEFAULT: None
         }
       }


def set_file_paths(args):
    paths = {}
    if not args.full_path:
        paths[INVENTORY_FILE_KEY] = INVENTORY_PATH + str(args.inventory_file)
        paths[SITE_FILE_KEY] = SITE_PATH + str(args.site_file)
    else:
        paths_raw = args.full_path.split(',')
        paths = {paths_raw[i].split('=')[0]: paths_raw[i].split('=')[1]
                 for i in range(len(paths_raw))}
    return paths


def send_alert(args, returncode, elapsed_time):
    if args.disable_alert is None:
        number = 'number=' + str(args.phone_number)
        message = ALERT_MSG.format(str(args.alert_message), str(returncode), str(elapsed_time))
        subprocess.Popen(['curl', 'http://textbelt.com/text', '-d', number, '-d', str(message)])

def get_time(elapsed):
    timestamp = {}
    timestamp[HOURS] = int(elapsed / 3600)
    timestamp[MINUTES] = int((elapsed % 3600) / 60)
    timestamp[SECONDS] = int(elapsed - ((timestamp[HOURS] * 3600) + (timestamp[MINUTES] * 60)))
    return timestamp

def play_alert_sound(timestamp):
    hdmi_audio = """osascript /Users/cjbaker/Development/AppleScripts/change_audio_output_to_hdmi.scpt"""
    headphones_audio = """osascript /Users/cjbaker/Development/AppleScripts/change_audio_output_to_headphones.scpt"""
    message = ' hey c bake ansible is done'
    message += ' It completed in {} hours and {} minutes'.format(str(timestamp[HOURS]), str(timestamp[MINUTES]))
    #os.system(hdmi_audio)
    os.system('say' + message)
    #os.system(headphones_audio)

def main(args):
    paths = set_file_paths(args)
    ssh_command = '/usr/local/bin/vagrant ssh ' + str(args.host) + ' -c '
    deploy_command = '/bin/ansible-playbook -i ' + str(paths[INVENTORY_FILE_KEY]) + ' ' + str(paths[SITE_FILE_KEY])
    if args.tags:
      deploy_command +=  ' --tags ' + str(args.tags)
    if args.sudo:
      deploy_command = 'sudo ' + deploy_command

    if args.vagrant_cwd:
        os.environ['VAGRANT_CWD'] = str(args.vagrant_cwd)
    print "Running Ansible Deployment... this may take some time"
    start = time.time()
    sp = subprocess.Popen(ssh_command.split() + [str(deploy_command)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while args.stdout:
        line = sp.stdout.readline()
        if not line:
            break
        print line.strip('\n')
        sys.stdout.flush()
    out, err = sp.communicate()
    timestamp = get_time(time.time() - start)
    execution_time = "{}h:{}m:{}s".format(str(timestamp[HOURS]), str(timestamp[MINUTES]), str(timestamp[SECONDS]))
    if args.audio_alert is not None:
        play_alert_sound(timestamp)
    send_alert(args, sp.returncode, execution_time)

    if args.stderr:
        print "Ansible Deployment Standard Error:"
        print err
    print "Ansible Deployment Returncode:"
    print sp.returncode
    print "Execution Time: {}".format(execution_time)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     usage='%(prog)s [options]',
                                     description=PROG_DESC)
    for opt in OPTS:
        option = OPTS[opt]
        parser.add_argument(option[SHORT], option[LONG],
                            help=option[HELP], action=option[ACTION],
                            required=option[REQUIRED],
                            default=option[DEFAULT])
    args = parser.parse_args()
    main(args)
