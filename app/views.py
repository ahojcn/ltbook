import io
import re
import random
import hashlib

from PIL import Image, ImageDraw, ImageFont
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader

from app import models


def index(request):
    """
    首页
    未登录：重定向到 login
    已登录：home 页面
    """
    context = {'status': 0, 'msg': '', 'data': {}}

    if request.method == 'GET':
        user_id = request.session.get('user_id')
        user = models.UserBase.objects.filter(id=user_id)

        if len(user) == 0:
            return redirect(to=login)

        user = user[0]
        # 获取用户基本信息
        context['data'] = {
            'user_id': user.id,
            'is_active': user.is_active,
            'email': user.email,
            'tel': user.tel,
            'reg_time': user.reg_time,
            'avatar': user.avatar,
            'gender': user.gender,
            'name': user.name,
        }

        return render(request, 'home.html', context=context)


def login(request):
    """
    登录
    """
    context = {'status': 0, 'msg': '', 'data': {}}

    if request.method == 'GET':
        return render(request, 'login.html', context=context)

    if request.method == 'POST':
        email = request.POST.get('email')
        pwd = request.POST.get('pwd')
        verify_code = request.POST.get('verify_code')

        if verify_code.upper() != request.session.get('verify_code', default='').upper():
            context['status'] = -1
            context['msg'] = '验证码有误'
            return render(request, 'login.html', context=context)

        user = models.UserBase.objects.filter(email=email)
        if len(user) == 0:
            context['status'] = -1
            context['msg'] = '邮箱有误'
            return render(request, 'login.html', context=context)

        user = user[0]

        if hashlib.md5(pwd.encode('utf-8')).hexdigest() != user.pwd:
            context['status'] = -1
            context['msg'] = '密码有误'
            return render(request, 'login.html', context=context)

        # 登录成功，重定向到首页
        request.session['user_id'] = user.id
        return redirect(to=index)


def active(request):
    """
    用户激活
    """
    context = {'status': 0, 'msg': '', 'data': {}}

    if request.method == 'GET':
        token = request.GET.get('token')
        s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 3600)

        try:
            info = s.loads(token)
            user_id = info['confirm']
            user = models.UserBase.objects.get(id=user_id)
            user.is_active = True
            user.save()
            context['status'] = 0
            context['msg'] = '激活成功'
            context['data'] = {'email': user.email}
        except SignatureExpired as e:
            context['status'] = -1
            context['msg'] = '链接过期'
        except Exception as e:
            print(e)
            context['status'] = -1
            context['msg'] = '未知错误'

        return render(request, 'active.html', context=context)

    if request.method == 'POST':
        """重新发送激活邮件"""
        email = request.POST.get('email')
        verify_code = request.POST.get('verify_code')

        if verify_code.upper() != request.session.get('verify_code', default='').upper():
            context['status'] = -1
            context['msg'] = '验证码有误'
            return render(request, 'active.html', context=context)

        user = models.UserBase.objects.filter(email=email)
        if len(user) == 0:
            context['status'] = -1
            context['msg'] = '没有此用户'
            return render(request, 'active.html', context=context)

        user = user[0]

        # 生成激活token，设置过期时间为 24 h
        s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 60 * 60 * 24)
        info = {'confirm': user.id}
        token = s.dumps(info)
        token = token.decode('utf8')

        # 发送激活邮件
        active_url = 'http://127.0.0.1:8000/active/?token=' + token
        t = loader.get_template('email_user_active.html')
        html = t.render({'email': email, 'active_url': active_url})
        send_mail('激活你的账号', '', settings.EMAIL_FROM, [email], html_message=html)

        context['status'] = 0
        context['msg'] = '已重新发送激活邮件，请注意查收！'

        return render(request, 'active.html', context=context)


def register(request):
    """
    注册
    """
    context = {'status': 0, 'msg': '', 'data': {}}

    if request.method == 'GET':
        return render(request, 'register.html', context=context)

    if request.method == 'POST':
        email = request.POST.get('email')
        pwd = request.POST.get('pwd')
        c_pwd = request.POST.get('c_pwd')
        verify_code = request.POST.get('verify_code')

        if verify_code.upper() != request.session.get('verify_code', default='').upper():
            context['status'] = -1
            context['msg'] = '验证码有误'
            return render(request, 'register.html', context=context)

        if pwd != c_pwd:
            context['status'] = -1
            context['msg'] = '两次密码不一致'
            return render(request, 'register.html', context=context)

        if len(pwd) < 6:
            context['status'] = -1
            context['msg'] = '密码太短'
            return render(request, 'register.html', context=context)

        if not re.match(r'^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            context['status'] = -1
            context['msg'] = '邮箱格式有误'
            return render(request, 'register.html', context=context)

        pwd_md5 = hashlib.md5(pwd.encode('utf-8')).hexdigest()

        try:
            user = models.UserBase.objects.create(email=email, pwd=pwd_md5, is_active=False)
        except Exception as e:
            print(e)
            context['status'] = -1
            context['msg'] = '邮箱已被注册'
            return render(request, 'register.html', context=context)

        # 生成激活token，设置过期时间为 24 h
        s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 60 * 60 * 24)
        info = {'confirm': user.id}
        token = s.dumps(info)
        token = token.decode('utf8')

        # 发送激活邮件
        active_url = 'http://127.0.0.1:8000/active/?token=' + token
        t = loader.get_template('email_user_active.html')
        html = t.render({'email': email, 'active_url': active_url})
        send_mail('激活你的账号', '', settings.EMAIL_FROM, [email], html_message=html)

        context['status'] = 0
        context['msg'] = '注册成功，已发送激活邮件，请注意查收！'
        return render(request, 'register.html', context=context)


def verify_code_img(request):
    """
    图片验证码

    GET: 获取图片验证码
    """

    if request.method == 'GET':
        width = 200
        height = 60

        bg_color = (random.randrange(20, 100), random.randrange(20, 100), 255)

        # 画布
        im = Image.new('RGB', (width, height), bg_color)
        # 画笔
        draw = ImageDraw.Draw(im)

        # 绘制噪点
        for i in range(0, 500):
            xy = (random.randrange(0, width), random.randrange(0, height))
            fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
            draw.point(xy, fill=fill)
        # 绘制线
        for i in range(0, 10):
            xy = (random.randrange(0, width), random.randrange(0, height))
            fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
            draw.line(xy, fill=fill)

        code = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0qwertyuiopasdfghjklzxcvbnm'
        # 随机选 4 个
        rand_str = ''
        for i in range(0, 4):
            rand_str += code[random.randrange(0, len(code))]

        # 构造字体对象
        font = ImageFont.truetype('static/font/LatienneSwaT.ttf', height, encoding='unic')
        # 构造字体颜色
        font_color = (255, random.randrange(0, 255), random.randrange(0, 255))
        # 绘制 4 个字
        draw.text((0, 0), rand_str[0], font=font, fill=font_color)
        draw.text((width / 4, 0), rand_str[1], font=font, fill=font_color)
        draw.text((width / 4 * 2, 0), rand_str[2], font=font, fill=font_color)
        draw.text((width / 4 * 3, 0), rand_str[3], font=font, fill=font_color)

        del draw

        # 存入 session
        request.session['verify_code'] = rand_str

        buf = io.BytesIO()
        im.save(buf, 'png')

        return HttpResponse(buf.getvalue(), 'image/png')
