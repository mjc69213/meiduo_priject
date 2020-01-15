import logging
from django.shortcuts import render, HttpResponse
from django.views import View
from django_redis import get_redis_connection
from django.db.utils import DatabaseError

from verifications.utils.captcha.captcha import captcha
from verifications.utils import constants

logger = logging.Logger('django')


class ImageCodeView(View):
    '''
    获取图形验证码
    '''

    def get(self, request, uid):
        text, img = captcha.generate_captcha()
        try:
            redis_handel = get_redis_connection('verify_code')
            redis_handel.setex(f'img_{uid}', constants.IMAGE_CODE_REDIS_EXPIRES, text)
            logger.info(text)
        except DatabaseError as e:
            logger.error(e)

        return HttpResponse(content=img, content_type='image/jpg')
