#!/usr/bin/env python

import argparse
import os
import shutil
import subprocess


ROOT_PATH = "c:\\"
SYSTEM_PYTHON_PATH = os.path.join(ROOT_PATH, "Python27")
SYSTEM_SCRIPTS_PATH = os.path.join(SYSTEM_PYTHON_PATH, "Scripts")
SYSTEM_PYTHON = os.path.join(SYSTEM_SCRIPTS_PATH, "python.exe")
PROJECT_PATH = os.path.join(ROOT_PATH, "winliberator")
VENV_PATH = os.path.join(PROJECT_PATH, "venv")
SCRIPTS_PATH = os.path.join(VENV_PATH, "Scripts")
PYTHON = os.path.join(SCRIPTS_PATH, "python.exe")
PIP = os.path.join(SCRIPTS_PATH, "pip.exe")
MANAGE = os.path.join(PROJECT_PATH, "manage.py")


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
    subprocess.check_call([os.path.join(SYSTEM_SCRIPTS_PATH, "virtualenv.exe"),
                           VENV_PATH, ],
                          shell=True)


def cmd_pip(args=[]):
    ''' Runs the virtualenv's pip command with specified arguments.
    '''
    args.insert(0, PIP)
    subprocess.check_call(args)


# Custom settings and commands start here
def cmd_run(args=[]):
    ''' Runs the server
    '''
    args.insert(0, PYTHON)
    args.insert(1, MANAGE)
    args.insert(2, "runwsgiserver")
    args.insert(3, "host=0.0.0.0")
    args.insert(4, "port=80")
    subprocess.check_call(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Director',
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
