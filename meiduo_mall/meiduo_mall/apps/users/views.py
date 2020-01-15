import logging
from django.shortcuts import render, redirect
from django.views import View
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError
from django.http import HttpResponseForbidden, HttpResponse
from django.urls import reverse
from django.contrib.auth import login

from  .models import User

logger = logging.Logger('django')
class UserForm(forms.Form):
    '''
    用户提交注册数据的后端验证
    '''
    username = forms.CharField(validators=[RegexValidator(r'^[a-zA-Z]\w{1,15}', '用户名格式不正确')])
    password = forms.CharField(max_length=6, validators=[RegexValidator(r'^\w{6,}', '密码长度不够')])
    password2 = forms.CharField(max_length=6, validators=[RegexValidator(r'^\w{6,}', '重复密码长度不够')])
    mobile = forms.CharField(max_length=11, validators=[RegexValidator(r'^1[35896]\d{9}', '手机号码格式不正确')])
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
            try:
                user = User.objects.create_user(**user_forms.cleaned_data)
                login(request,user)
                return redirect(reverse('home:index'))
            except DatabaseError as e:
                logger.error(e)
                return render(request, 'register.html', {'error': '注册失败'})
        return HttpResponseForbidden('参数不正确')
