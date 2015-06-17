#!/usr/bin/env python

import argparse
from ConfigParser import ConfigParser
import os
import shutil
import subprocess
import sys


config = ConfigParser()
config.read(os.path.join('do', 'config.ini'))
SYSTEM_PYTHON_PATH = config.get('Config', 'SYSTEM_PYTHON_PATH')
SYSTEM_SCRIPTS_PATH = config.get('Config', 'SYSTEM_SCRIPTS_PATH')
SYSTEM_PYTHON = config.get('Config', 'SYSTEM_PYTHON')
PROJECT_PATH = config.get('Config', 'PROJECT_PATH')
VENV_PATH = config.get('Config', 'VENV_PATH')
SCRIPTS_PATH = config.get('Config', 'SCRIPTS_PATH')
PYTHON = config.get('Config', 'PYTHON')
PIP = config.get('Config', 'PIP')
MANAGE = config.get('Config', 'MANAGE')


def cmd_python(args=[]):
    ''' Runs the virtualenv's python command with specified arguments.
        Useful for running infrequently used or one-off commands.
    '''
    args.insert(0, PYTHON)
    subprocess.check_call(args)

def cmd_install(args=[]):
    ''' Sets up a virtualenv.
        Installs packages from requirements.txt.
    '''
    cmd_create_virtualenv(args)
    cmd_pip(['install', '-r', 'requirements.txt'])

def cmd_create_virtualenv(args=[]):
    ''' Destroys old virtualenv.
        Creates new virtualenv.
    '''
    print("Removing old venv.")
    shutil.rmtree(VENV_PATH, ignore_errors=True)
    print("Creating new venv.")
    venv_exe = os.path.join(SYSTEM_SCRIPTS_PATH, "virtualenv.exe")
    if not os.path.isfile(venv_exe):
        print("*** Error: You need to install virtualenv into your system Python. ***")
        print("Try doing the following with administrator rights: ")
        print("$ cd {}".format(SYSTEM_SCRIPTS_PATH))
        print("$ pip install --upgrade pip")
        print("$ pip install virtualenv")
        sys.exit(1)
    subprocess.check_call([venv_exe,
                           VENV_PATH, ],
                          shell=True)

def cmd_pip(args=[]):
    ''' Runs the virtualenv's pip command with specified arguments.
    '''
    args.insert(0, PIP)
    subprocess.check_call(args)

# Custom settings and commands start here
def cmd_build_dev(args=[]):
    cmd_install()
    cmd_flush_db()
    cmd_migrate()
    cmd_load_dev_fixtures()

def cmd_flush_db(args=[]):
    ''' Flushes the Django database
    '''
    args.insert(0, PYTHON)
    args.insert(1, MANAGE)
    args.insert(2, "flush")
    args.insert(3, "--noinput")
    subprocess.check_call(args)

def cmd_collectstatic(args=[]):
    ''' Collects the static files
    '''
    args.insert(0, PYTHON)
    args.insert(1, MANAGE)
    args.insert(2, "collectstatic")
    subprocess.check_call(args)

def cmd_load_dev_fixtures(args=[]):
    '''  Loads winliberator/fixtures/my_dsns.json into database
    '''
    args.insert(0, PYTHON)
    args.insert(1, MANAGE)
    args.insert(2, "loaddata")
    args.insert(3, "dev_user")
    args.insert(4, "my_dsns")
    subprocess.check_call(args)

def cmd_migrate(args=[]):
    ''' Runs Django migrations
    '''
    args.insert(0, PYTHON)
    args.insert(1, MANAGE)
    args.insert(2, "migrate")
    subprocess.check_call(args)

def cmd_run_dev(args=[]):
    ''' Runs the server
    '''
    args.insert(0, PYTHON)
    args.insert(1, MANAGE)
    args.insert(2, "runserver")
    subprocess.check_call(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Do',
                                     description='Run a command.')
    parser.add_argument('command', help='The command you want to run.')
    parser.add_argument('args',
                        nargs=argparse.REMAINDER,
                        help='Arguments to the command.')
    pargs = parser.parse_args()

    command_pargs = pargs.command.lower()
    command_cmd = "cmd_{}".format(command_pargs)
    try:
        locals()[command_cmd](pargs.args)
    except KeyError:
        print("Unknown command: {}".format(command_pargs))
