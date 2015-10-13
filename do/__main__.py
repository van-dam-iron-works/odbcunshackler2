#!/usr/bin/env python

import argparse
from configparser import ConfigParser
import os
import shutil
import subprocess
import sys


# Get the config and create commonly-used command paths
config = ConfigParser()
config.read(os.path.join('do', 'config.ini'))

SYSTEM_PYTHON_PATH = config.get('Config', 'SYSTEM_PYTHON_PATH')
SYSTEM_SCRIPTS_PATH = os.path.join(SYSTEM_PYTHON_PATH, 'Scripts')
SYSTEM_PYTHON = os.path.join(SYSTEM_PYTHON_PATH, 'python')
VIRTUALENV_CMD = os.path.join(SYSTEM_SCRIPTS_PATH, 'virtualenv.exe')

PROJECT_PATH = config.get('Config', 'PROJECT_PATH')
MANAGE = os.path.join(PROJECT_PATH, 'manage.py')

VENV_PATH = config.get('Config', 'VENV_PATH')
SCRIPTS_PATH = os.path.join(VENV_PATH, 'Scripts')
PYTHON = os.path.join(SCRIPTS_PATH, 'python')
PIP = os.path.join(SCRIPTS_PATH, 'pip')


def build_cmd(cmd_seed=[], *args):
    """
    Builds the real command by inserting the provided *args in front of
    command pieces in the seed
    :param cmd_seed: Extra arguments to the command we'll insert in front of
    :param args: Pieces of the command to insert
    :return: command with everything in place
    """
    insertion_point = 0
    for arg in args:
        cmd_seed.insert(insertion_point, arg)
        insertion_point += 1
    return cmd_seed


def cmd_python(args=[]):
    """ Runs the virtualenv's python command with specified arguments.
        Useful for running infrequently used or one-off commands.
    """
    cmd = build_cmd(args, PYTHON)
    subprocess.check_call(cmd)


def cmd_install(args=[]):
    """ Sets up a virtualenv.
        Installs packages from requirements.txt.
    """
    cmd_create_virtualenv(args)
    cmd_pip(['install', '-r', 'requirements.txt'])


def cmd_create_virtualenv(args=[]):
    """ Destroys old virtualenv.
        Creates new virtualenv.
    """
    print("Removing old venv.")
    shutil.rmtree(VENV_PATH, ignore_errors=True)
    print("Creating new venv.")
    if not os.path.isfile(VIRTUALENV_CMD):
        print("*** Error:",
              "You need to install virtualenv into your system Python. ***")
        print("Try doing the following. You may need administrator rights: ")
        print("cd {}".format(SYSTEM_SCRIPTS_PATH))
        print("pip install --upgrade pip")
        print("pip install virtualenv")
        sys.exit(1)
    cmd = build_cmd(args, VIRTUALENV_CMD, VENV_PATH)
    subprocess.check_call(cmd, shell=True)


def cmd_pip(args=[]):
    """ Runs the virtualenv's pip command with specified arguments.
    """
    cmd = build_cmd(args, PIP)
    subprocess.check_call(cmd)


def cmd_flake8(args=[]):
    """ Runs the flake8 checker
    """
    cmd = build_cmd(args,
                    os.path.join(SCRIPTS_PATH, 'flake8'),
                    '--max-complexity=12',
                    '--exclude=migrations,static',
                    PROJECT_PATH)
    subprocess.call(cmd)


# Custom settings and commands start here
def cmd_build_dev(args=[]):
    cmd_install()
    cmd_flush_db()
    cmd_migrate()
    cmd_load_dev_fixtures()


def cmd_flush_db(args=[]):
    """ Flushes the Django database
    """
    cmd = build_cmd(args, PYTHON, MANAGE, "flush", "--noinput")
    print(cmd)
    subprocess.check_call(cmd)


def cmd_collectstatic(args=[]):
    """ Collects the static files
    """
    cmd = build_cmd(args, PYTHON, MANAGE, "collectstatic")
    subprocess.check_call(cmd)


def cmd_load_dev_fixtures(args=[]):
    """  Loads odbcunshackler2/fixtures/ into database
    """
    cmd = build_cmd(args, PYTHON, MANAGE, "loaddata", "dev_user", "my_dsns")
    subprocess.check_call(cmd)


def cmd_migrate(args=[]):
    """ Runs Django migrations
    """
    cmd = build_cmd(args, PYTHON, MANAGE, "migrate")
    subprocess.check_call(cmd)


def cmd_run(args=[]):
    """ Runs the server in development mode (default)
    """
    cmd = build_cmd(args, PYTHON, MANAGE, "runserver")
    subprocess.check_call(cmd)

def cmd_run_prod(args=[]):
    """ Runs the server in production mode
    """
    waitress_serve = os.path.join(SCRIPTS_PATH, 'waitress-serve')
    cmd = build_cmd(args, waitress_serve, "--port=80", "odbcunshackler2.wsgi:application")
    subprocess.check_call(cmd)


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
