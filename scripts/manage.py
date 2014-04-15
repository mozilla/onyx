#!/usr/bin/env python
from flask.ext.script import Manager
from onyx.utils import environment_manager_create, GunicornServerCommand

manager = Manager(environment_manager_create)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command('runserver', GunicornServerCommand())

if __name__ == "__main__":
    manager.run()
