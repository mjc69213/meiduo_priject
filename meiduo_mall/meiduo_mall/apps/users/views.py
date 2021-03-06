import logging
from django.shortcuts import render, redirect
from django.views import View
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth import login
from django_redis import get_redis_connection

from .models import User
from users.utils.response_code import RETCODE

logger = logging.Logger('django')
redis_handel = get_redis_connection('verify_code')


class UserForm(forms.Form):
    '''
    用户提交注册数据的后端验证
    '''
    username = forms.CharField(validators=[RegexValidator(r'^[a-zA-Z]\w{1,15}', '用户名格式不正确')])
    password = forms.CharField(max_length=6, validators=[RegexValidator(r'^\w{6,}', '密码长度不够')])
    password2 = forms.CharField(max_length=6, validators=[RegexValidator(r'^\w{6,}', '重复密码长度不够')])
    mobile = forms.CharField(max_length=11, validators=[RegexValidator(r'^1[35896]\d{9}', '手机号码格式不正确')])
    sms_code = forms.CharField()
    allow = forms.CharField(validators=[RegexValidator(r'on', '没有勾选同意协议')])

    def clean(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password2')
        if p1 != p2:
            self.add_error('password2', '两次密码不致')
            raise ValidationError('两次密码不一致')
        return self.cleaned_data


class RegisterView(View):
    '''
    用户注册
    '''

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        user_forms = UserForm(request.POST)
        if user_forms.is_valid():
            # 保存检验过的数据
            user_forms.cleaned_data.pop('allow')
            user_forms.cleaned_data.pop('password2')
            phone = user_forms.cleaned_data.get('mobile')
            sms_server = redis_handel.get(f'sms_{phone}')
            sms_cli = user_forms.cleaned_data.get('sms_code')
            if sms_server is None:
                return render(request, 'register.html', {'error': '短信验证码失效'})
            if sms_server.decode() != sms_cli:
                return render(request, 'register.html', {'error': '短信验证码错误'})
            try:
                user_forms.cleaned_data.pop('sms_code')
                user = User.objects.create_user(**user_forms.cleaned_data)
                login(request, user)
                return redirect(reverse('home:index'))
            except DatabaseError as e:
                logger.error(e)
                return render(request, 'register.html', {'error': '注册失败'})
        return HttpResponseForbidden('参数不正确')


class CheckUserRepeat(View):
    '''
    检查用户名重复
    '''

    def get(self, request, uname):
        try:
            count = User.objects.filter(username=uname).count()
            if count == 1:
                return JsonResponse({'code': RETCODE.OK, 'msg': '该用户已经被注册', 'count': count})
            return JsonResponse({'code': RETCODE.OK, 'msg': '该用户可以被注册', 'count': count})
        except DatabaseError as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'msg': '查询错误'})


class CheckPhoneRepeat(View):
    '''
    检查手机号重复
    '''

    def get(self, request, phone):
        try:
            count = User.objects.filter(mobile=phone).count()
            if count == 1:
                return JsonResponse({'code': RETCODE.OK, 'msg': '该手机已经被注册', 'count': count})
            return JsonResponse({'code':RETCODE.OK, 'msg': '该手机可以注册', 'count': count})
        except DatabaseError as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'msg': '查询错误'})

