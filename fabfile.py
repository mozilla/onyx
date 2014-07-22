import os
import time
from datetime import datetime
from distutils.util import strtobool
from functools import wraps

from fabric import colors
from fabric.api import env, run, local, require, put, abort, sudo, settings

env.path = "/var/www/onyx"
env.user = "root"
env.app_user = "onyx"
env.num_keep_releases = 10
env.use_ssh_config = True
env.release = time.strftime("%Y-%m-%d-%H-%M-%S", datetime.utcnow().timetuple())
env.release_dir = os.path.join(env.path, env.release)

env.zip_path = None


def section(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print colors.cyan('Running section "{}"'.format(f.__name__), bold=True)
        f(*args, **kwargs)
        print
    return wrapper


### Utility

@section
def upload_from_dist(run_setuptools=False):
    """
    Create zip, send over the wire and unzip
    """
    require("release", provided_by=[deploy_cold, deploy])
    if run_setuptools:
        local("python setup.py sdist")
    # get last modified file
    out = local("ls -t ./dist/*.gz | head -1", capture=True)

    global env
    arch_path = out.stdout.strip()
    env.arch_filename = os.path.basename(arch_path)
    env.app_dirname = env.arch_filename.replace('.tar.gz', '')
    put(arch_path, "/tmp/")

    sudo("mkdir %(release_dir)s" % env, user=env.app_user)
    sudo("tar -C %(release_dir)s -xf /tmp/%(arch_filename)s" % env, user=env.app_user)
    run("rm /tmp/%(arch_filename)s" % env)


@section
def set_symlinks():
    require("release", provided_by=[deploy, deploy_cold])
    sudo("if [ -h %(path)s/previous ]; then rm %(path)s/previous; fi" % env, user=env.app_user)
    sudo("if [ -h %(path)s/current ]; then mv %(path)s/current %(path)s/previous; fi" % env, user=env.app_user)
    sudo("ln -s %(release_dir)s/%(app_dirname)s %(path)s/current" % env, user=env.app_user)


@section
def setup_virtualenv():
    require("release", provided_by=[deploy, deploy_cold])
    put("./setup-project.sh", "/tmp/" % env)
    sudo("cp /tmp/setup-project.sh %(release_dir)s/%(app_dirname)s" % env, user=env.app_user)
    run("rm /tmp/setup-project.sh")
    sudo("export MOZ_ONYX_PROD=1; cd %(release_dir)s/%(app_dirname)s && bash ./setup-project.sh" % env, user=env.app_user)


@section
def clean_release_dir():
    """
    Delete releases if the number of releases to keep has gone beyond the threshold set by num_keep_releases
    """
    if env.num_keep_releases > 1:
        # keep at least 2 releases: one previous and one current
        releases = run("find %(path)s -maxdepth 1 -mindepth 1 -type d | sort" % env).split()
        if len(releases) > env.num_keep_releases:
            delete_num = len(releases) - env.num_keep_releases
            delete_list = " ".join(releases[:delete_num])
            sudo("rm -rf {0}".format(delete_list), user=env.app_user)


### Tasks

@section
def deploy_cold(run_setuptools):
    """
    Deploy code but don"t change current running version
    """
    upload_from_dist(run_setuptools)
    setup_virtualenv()


@section
def deploy(run_setuptools=False):
    """
    Deploy code, set symlinks and restart supervisor
    """
    deploy_cold(run_setuptools)
    clean_release_dir()
    set_symlinks()
    restart_processes()


@section
def restart_processes():
    with settings(warn_only=True):
        reload_cmd = sudo("supervisorctl reload")
        if reload_cmd.return_code != 0:
            # if reload didn't work, attempt to start supervisor
            # e.g. for first run after install
            sudo("/etc/init.d/supervisor start")

def to_bool(value):
    if not isinstance(value, bool):
        return strtobool(value)
    else:
        return value


def build():
    test()
    flake()
    package()


def test(config="nose.cfg", debug_errors=False, debug_failures=False):
    """
    Run automated tests.
    If debug_errors is provided as a truey value, will drop on debug prompt as
    soon as an exception bubbles out from the tests.
    If debug_failures is provided as a truey value, will drop on debug prompt
    as soon as an assertion fails.
    """
    command = "nosetests --config={}".format(config)
    if to_bool(debug_errors):
        command += " --ipdb"
    if to_bool(debug_failures):
        command += " --ipdb-failures"
    local(command)


def flake(config="flake8.cfg"):
    local("flake8 . --config={}".format(config))


def package(clean=True):
    if to_bool(clean):
        local("rm -rf build/")
    local("python setup.py build")
