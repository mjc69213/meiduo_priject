#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from celery_tasks.main import celery_app

from celery_tasks.sms.yuntongxun.ccp_sms import CCP
from . import constants


@celery_app.task(name='ccp_send_sms_code')
def ccp_send_sms_code(phone, sms_code):
    return CCP().send_sms_template(phone, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], '1')