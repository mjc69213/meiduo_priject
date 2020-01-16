#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from celery import Celery

print(sys.path)
celery_app = Celery('meiduo')
celery_app.config_from_object('celery_tasks.config')
celery_app.autodiscover_tasks(['celery_tasks.sms'])