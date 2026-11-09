import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory_site.settings")
django.setup()

from django.test import Client
from django.test.utils import setup_test_environment

setup_test_environment()      # lets the client use the host name "testserver"
client = Client()
