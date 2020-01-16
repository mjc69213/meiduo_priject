import logging
import random
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection
from django.db.utils import DatabaseError
from django import forms
from django.core.validators import RegexValidator

from verifications.utils.captcha.captcha import captcha
from verifications.utils import constants
from verifications.utils.response_code import RETCODE
from verifications.utils.yuntongxun.ccp_sms import CCP
from celery_tasks.sms.tasks import ccp_send_sms_code


logger = logging.Logger('django')
redis_handel = get_redis_connection('verify_code')
p1 = redis_handel.pipeline()

class ImageCodeView(View):
    '''
    获取图形验证码
    '''

    def get(self, request, uid):
        text, img = captcha.generate_captcha()
        try:
            redis_handel.setex(f'img_{uid}', constants.IMAGE_CODE_REDIS_EXPIRES, text)
            logger.info(text)
        except DatabaseError as e:
            logger.error(e)

        return HttpResponse(content=img, content_type='image/jpg')

class SMSForm(forms.Form):
    '''
    短信验证码的参数检验
    '''
    uuid = forms.CharField(validators=[RegexValidator(r'\w{8}(-\w{4}){3}-\w{12}', 'uuid格式不正确')])
    image_code = forms.CharField(validators=[RegexValidator(r'\w{4}', '图形验证码格式不正确')])

class SMSCodeView(View):
    '''
    短信验证码
    '''

    def get(self, request, phone):
        parms_form = SMSForm(request.GET)
        if parms_form.is_valid():
            # 在redis中取值会有两种情况，一是取不到过期 二是和客户端传过来不同
            img_cli = parms_form.cleaned_data.get('image_code')
            uid = parms_form.cleaned_data.get('uuid')
            img_server = redis_handel.get(f'img_{uid}')
            # 后端限制60秒内发送短信限制
            send_flage = redis_handel.get(f'send_{phone}')
            if send_flage:
                return JsonResponse({'code': RETCODE.IMAGECODEERR, 'msg': '发送短信过于频繁'})
            # 防止用户恶意猜图形验证码，需要删除redis中的验证码
            redis_handel.delete(f'img_{uid}')
            if img_server is None:
                return JsonResponse({'code':RETCODE.IMAGECODEERR, 'msg': '验证码过期'})
            # 因为从redis中取出的数据是bytes类型的需要进行转换
            img_server = img_server.decode()
            if img_server.lower() != img_cli.lower():
                return JsonResponse({'code': RETCODE.IMAGECODEERR, 'msg': '验证码错误'})
            random_num = '%06d' % random.randint(1, 999999)
            logger.info(random_num)
            # ret = CCP().send_sms_template(phone, [random_num, constants.SMS_CODE_REDIS_EXPIRES // 60], '1')
            ret = ccp_send_sms_code(phone, random_num)
            if ret == -1:
                return JsonResponse({'code': RETCODE.OK, 'msg': '短信发送失败'})
            try:
                p1.setex(f'sms_{phone}', constants.SMS_CODE_REDIS_EXPIRES, random_num)
                p1.setex(f'send_{phone}', constants.SEND_SMS_CODE_INTERVAL, 1)
                p1.execute()
            except DatabaseError as e:
                logger.error(e)
                return JsonResponse({'code': RETCODE.DBERR, 'msg': '未知错误'})
            return JsonResponse({'code': RETCODE.OK, 'msg': '短信发送成功'})
