#!/usr/bin/env python
from flask.ext.script import Manager
from onyx.utils import environment_manager_create, GunicornServerCommand, LogCommand

manager = Manager(environment_manager_create)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command('runserver_gunicorn', GunicornServerCommand())
manager.add_command('log', LogCommand)

if __name__ == "__main__":
    manager.run()
