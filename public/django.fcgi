#!/usr/bin/env python
import os, sys
import site

os.environ['VIRTUAL_ENV'] = '/home/%(account_name)s/.virtualenvs/%(virtualenv_name)s/'
# TODO: variable in venv variable
venv = '/home/%(account_name)s/.virtualenvs/%(virtualenv_name)s/bin/activate_this.py'
execfile(venv, dict(__file__=venv))

import glob
for dir in glob.glob(os.environ['VIRTUAL_ENV'] + '/src/*'):
    if os.path.isdir(dir):
        site.addsitedir(dir)

# hack for django-moderation project
site.addsitedir('/home/%(account_name)s/.virtualenvs/%(virtualenv_name)s/src/django-moderation/src')

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_DIR)
sys.path.insert(0, os.path.dirname(_PROJECT_DIR))

_PROJECT_NAME = _PROJECT_DIR.split('/')[-1]
os.environ['DJANGO_SETTINGS_MODULE'] = _PROJECT_NAME+".settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
