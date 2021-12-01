
from django.shortcuts import render, redirect
from .models import User
from .forms import UserForm, RegisterForm
from django.db import connection


def index(request):
    pass
    return render(request, 'user/index.html')


def login(request):
    if request.session.get('is_login',None):
        return redirect('/manager/')
 
    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "Please check the content!"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.raw('SELECT * FROM user WHERE u_name=%s',[username])[0]
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.uid
                    request.session['user_name'] = user.u_name
                    if user.user_type == 'Manager':
                        request.session['manager'] = True
                    else:
                        request.session['manager'] = False
                    return redirect('/manager/')

                else:
                    message = "Wrong password!"
            except:
                message = "User does not exist!"
        return render(request, 'user/login.html', locals())
 
    login_form = UserForm()
    return render(request, 'user/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/manager/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "Pleace check your input!"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "The two passwords entered are different!"
                return render(request, 'user/register.html', locals())
            else:
                same_name_user = User.objects.raw('SELECT * FROM user WHERE u_name=%s',[username])
                if same_name_user:  # 用户名唯一
                    message = 'The user already exists, please select a user name again!'
                    return render(request, 'user/register.html', locals())
                same_email_user = User.objects.raw('SELECT * FROM user WHERE email=%s',[email])
                if same_email_user:  # 邮箱地址唯一
                    message = 'This email address has already been registered, please use another email address!'
                    return render(request, 'user/register.html', locals())
 
                # 当一切都OK的情况下，创建新用户

                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO user(u_name, password, email) VALUES (%s,%s,%s)",[username, password1, email])

                # new_user = User.objects.create()
                # new_user.u_name = username
                # new_user.password = password1
                # new_user.email = email
                # # new_user.sex = sex
                # new_user.save()
                return redirect('/users/login/')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'user/register.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/manager/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/manager/")