from distutils.util import strtobool

from fabric.api import local


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
