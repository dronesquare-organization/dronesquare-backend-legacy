from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backendAPI.settings')

app = Celery('d2projects', broker='amqp://admin:admin@localhost:8080/test', backend='amqp://admin:admin@localhost:8080/test')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()