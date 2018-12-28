import os
import random
import re

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect
import base64

from aj_app.ext import db
from aj_app.models import User
from utils import status_code

user_blue = Blueprint('user_blue', __name__, url_prefix='/user/')


@user_blue.route('/register/',methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        '''获取注册用户提交的数据,这里是获取POST提交的参数，所以要用request.form,前端提交过来的数据是手机号，图片验证码，密码，确认密码'''
        mobile = request.form.get('mobile')
        imageCode = request.form.get('imageCode')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        '''验证数据的完整性'''
        if not all([mobile, imageCode, password, password2]):
            return jsonify(status_code.USER_NOT_ALL)
        '''验证手机号码是否合法，使用正则表达式'''
        if not re.match(r'^1[3456789]\d{9}$', mobile):
            return jsonify(status_code.USER_MOBILE_ERROR)
        '''验证校验码是否正确'''
        if session.get('code') != imageCode:
            return jsonify(status_code.USER_IMAGECODE_ERROR)
        '''验证密码是否相等'''
        if password != password2:
            return jsonify(status_code.USER_PASSWORD_ERROR)
        '''验证用户是否已经存在，通过填入的手机号码去找用户对象，如果能找到用户对象，则证明用户已经存在了'''
        if User.query.filter(User.phone == mobile).count():
            return jsonify(status_code.USER_ERROR)
        '''上述验证都通过之后，就可以新建一个用户对象了，用户的phone和name都采用手机号码'''
        user = User()
        user.phone = mobile
        user.password = password
        user.name = mobile
        try:
            user.add_update()  # add_update()是父类里面定义的一个对象方法，具体参加User()表
            session['code'] = ''
            return jsonify(status_code.SUCCESS)
        except:
            return jsonify(status_code.DATABASE_ERROR)


@user_blue.route('/get_code/', methods=['GET'])
def get_code():
    """
    生成验证码
    """
    code = ''
    s = '123456789qwertyuipasdfghjklzxcvbnm'
    for i in range(4):
        code += random.choice(s)
    session['code'] = code

    # 定义使用Image类实例化一个长为120px,宽为40px,基于RGB的(255,255,255)颜色的图片
    img1 = Image.new(mode="RGB", size=(120, 40), color=(255, 255, 255))
    # 实例化一支画笔
    draw1 = ImageDraw.Draw(img1, mode="RGB")
    for i in range(200):
        draw1.point(
            (random.randint(0, 120), random.randint(0, 40)),  # 坐标
            fill=(0, 0, 0)  # 颜色
        )

    # 定义要使用的字体
    font1 = ImageFont.truetype("../../static/fonts/ALGER.TTF", 28)

    for i in range(len(code)):
        # 每循环一次,从a到z中随机生成一个字母或数字
        # 65到90为字母的ASCII码,使用chr把生成的ASCII码转换成字符
        # str把生成的数字转换成字符串
        char1 = code[i]

        # 每循环一次重新生成随机颜色
        color1 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # 把生成的字母或数字添加到图片上
        # 图片长度为120px,要生成5个数字或字母则每添加一个,其位置就要向后移动24px
        draw1.text([6+i * 30, 5], char1, color1, font=font1)
    # 把生成的图片保存为"pic.png"格式
    path = f'./static/code/{code}.png'
    with open(path, 'wb') as f:
        img1.save(f,format='png')
    with open(path, 'rb') as f:
        image = str(base64.b64encode(f.read()))[2:-1]
    os.remove(path)
    return jsonify(code=200, msg='请求成功',img=image)


@user_blue.route('/login/',methods=['GET', 'POST'])
def login():
    # 提供登录界面
    if request.method == 'GET':
        return render_template('login.html')
    # 接收登录信息
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        password = request.form.get('password')

        '''验证数据的完整性'''
        if not all([mobile, password]):
            return jsonify(status_code.USER_NOT_ALL)
        '''验证手机号是否合法'''
        if not re.match(r'^1[3456789]\d{9}$', mobile):
            return jsonify(status_code.USER_MOBILE_ERROR)
        user = User.query.filter_by(phone=mobile).first()
        if not user:
            # 用户未注册
            return jsonify(status_code.USER_LOGIN_PHONE_NOT_EXISTS)
        if not user.check_password(password):
            # 密码错误
            return jsonify(status_code.USER_LOGIN_PASSWORD_ERROR)
        # 登录成功
        session['user_id'] = user.id
        return jsonify(status_code.SUCCESS)

@user_blue.route('/my/', methods=['GET'])
def my_home():
    if request.method == 'GET':
        return render_template('my.html')

@user_blue.route('/user/', methods=['GET'])
def user_information():
    # 获取用户基本信息
    if request.method == 'GET':
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        return jsonify({'user':user.to_basic_dict()})


@user_blue.route('/profile/', methods=['GET', 'PATCH', 'PUT'])
def profile():
    # 返回个人基本信息修改界面
    if request.method == 'GET':
        return render_template('profile.html')
    # 修改用户头像
    if request.method == 'PATCH':
        files = request.files.get('avatar')
        if not files:
            # 空文件
            return jsonify({'code':11001, 'msg':'图片不能为空'})
        #验证文件类型是否允许
        allow_suffix = ['jpg', 'png', 'jpeg', 'gif', 'bmp']
        file_suffix = files.filename.split(".")[-1]
        if file_suffix not in allow_suffix:
            return jsonify({"code": 11000, "msg": "图片格式不正确"})
        # 存储图片
        user_id = session['user_id']
        user = User.query.filter_by(id = user_id).first()
        path = f'./static/upload/avatar/{user_id}'+'.'+file_suffix
        # with open(path, 'wb') as f:
        #     f.write(files.read())
        # 保存图片
        files.save(path)
        user.avatar = path[1:]
        user.add_update()
        return jsonify({'code':200,'url':path[1:]})

    # 修改用户用户名
    if request.method == 'PUT':
        username = request.form.get('name')
        # 判断用户名是否和法
        if not username:
            return jsonify(status_code.PARAMS_ERROR)
        # 判断是否重名
        if User.query.filter_by(name=username).count():
            return jsonify(status_code.USER_REGISTER_USER_IS_EXSITS)
        else:
            # 修改用户用户名
            user_id = session.get('user_id')
            user = User.query.filter_by(id=user_id).first()
            user.name = username
            user.add_update()
            return jsonify(status_code.SUCCESS)
        pass





@user_blue.route('/auth/', methods=['GET', 'PATCH', 'PUT'])
def auth():
    if request.method == 'GET':
        return render_template('auth.html')


@user_blue.route('/auths/', methods=['GET', 'PUT'])
def auths():
    # 返回用户实名认证信息
    if request.method == 'GET':
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        return jsonify({'id_name':user.id_name, 'id_card':user.id_card})

    # 上传用户实名认证信息
    if request.method == 'PUT':
        id_name = request.form.get('id_name')
        id_card = request.form.get('id_card')
        '''验证数据完整性'''
        if not all([id_name, id_card]):
            return jsonify(status_code.USER_NOT_ALL)
        '''校验名字是否合法'''
        if not re.match(r'^([\u4e00-\u9fa5]{1,20}|[a-zA-Z\.\s]{1,20})$', id_name):
            return jsonify(status_code.USER_REGISTER_AUTH_NAME_ERROR)
        '''检验身份证号码是否合法'''
        pattern = re.compile(r'^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$')
        if not re.match(pattern, id_card):
            return jsonify(status_code.USER_REGISTER_AUTH_ERROR)
        '''保存用户实名认证信息'''
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        user.id_name = id_name
        user.id_card = id_card
        user.add_update()
        return jsonify(status_code.SUCCESS)



@user_blue.route('/logout/', methods=['DELETE'])
def logout():
    if request.method == 'DELETE':
        session['user_id'] = ''
        return jsonify(status_code.SUCCESS)







@user_blue.before_request
def my_before_request():
    if not session.get('user_id') and request.path not in ['/user/login/','/user/register/', '/user/get_code/']:
        return redirect(url_for('user_blue.login'))