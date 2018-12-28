import os
import random
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for
from flask_sqlalchemy import Pagination
from sqlalchemy import or_, not_

from aj_app.models import Area, House, Facility, User, HouseImage, Order
from utils import status_code

house_blue = Blueprint('house_blue', __name__, url_prefix='/house/')

@house_blue.route('/hindex/',methods=['GET'])
def hindex():
    '''返回最新的5个房屋信息'''
    length = House.query.count()
    hlist = House.query.filter(House.id.in_(random.sample(range(0, length), 5))).all()
    hlist2 = [house.to_dict() for house in hlist]
    '''查找地区信息'''
    area_list = Area.query.all()
    area_dict_list = [area.to_dict() for area in area_list]
    '''当用户已经处于登录状态的时候，返回用户的名字，房屋信息和地区信息'''
    if session.get('user_id'):
        user = User.query.filter_by(id=session['user_id']).first()
        user_name = user.name
        code = status_code.OK
        return jsonify(code=code, name=user_name, hlist=hlist2, alist=area_dict_list)
    '''当游客访问的时候，返回房屋信息和地区信息'''
    return jsonify(hlist=hlist2, alist=area_dict_list)


@house_blue.route('/index/',methods=['GET'])
def index():
    if request.method == 'GET':

        return render_template('index.html')


@house_blue.route('/search/',methods=['GET'])
def search():
    if request.method == 'GET':
        return render_template('search.html')


@house_blue.route('/my_search/',methods=['GET'])
def my_search():
    if request.method == 'GET':
        # 获取get传过来的参数
        aid = request.args.get('aid')
        if not aid:
            aid = 1
        name = request.args.get('name')
        sd = request.args.get('sd')
        ed = request.args.get('ed')
        sk = request.args.get('sk')
        # 判断是否有请求页参数，如果无，默认为1
        if request.args.get('page'):
            page = int(request.args.get('page'))
        else:
            page = 1
        # 判断是否有每页多少数据的参数，如果无，默认为10
        if request.args.get('per_page'):
            per_page = int(request.args.get('per_page'))
        else:
            per_page = 10

        # 获取所有对象
        houses = House.query
        # 开始时间过滤
        if sd:
            sd = datetime.strptime(sd, '%Y-%m-%d')
            # 找出不符合要求的house_id
            orders = Order.query.filter(or_(Order.status=='REJECTED',Order.status=='CANCELED', Order.status=='COMPLETE', Order.status=='WAIT_COMMENT')).filter(Order.end_date > sd).all()
            houses_id = []
            for item in orders:
                houses_id.append(item.house_id)
            houses = houses.filter(not_(House.id in houses_id))
        # 结束时间过滤
        if ed:
            ed = datetime.strptime(ed, '%Y-%m-%d')
            days = (ed - sd).days + 1
            houses = houses.filter(or_(House.max_days==0, House.max_days>=days))
        # 区域过滤
        if aid:
            houses = houses.filter_by(area_id=aid)
        # 排序规则
        if sk:
            if sk == 'price-inc':
                houses = houses.order_by('price')
            elif sk == 'price-des':
                houses = houses.order_by('-price')
            elif sk == 'new':
                houses = houses.order_by('-id')
            elif sk == 'booking':
                houses = houses.order_by('order_count')
        paginate = houses.paginate(page, per_page)
        # 获取分页后的房间信息
        houses = paginate.items
        # 定义转换格式的接收变量
        house_info=[]
        for house in houses:
            # 跳转格式
            user = User.query.filter_by(id=house.user_id).first()
            house.landlord_url = user.avatar
            house = house.to_dict()
            house_info.append(house)
        # 获取页码列表
        pages_iter = []
        for item in paginate.iter_pages():
            pages_iter.append(item)
        return jsonify(code=status_code.OK, house_info=house_info, paginate_pages=paginate.pages, paginate_page=paginate.page, iter_pages = pages_iter, aid=aid)


'''接收前端发送的ajax请求，查询数据库中关于房屋设施和所处地区环境的数据，返回给前端'''
@house_blue.route('/area_facility/',methods=['GET'])
def area_facility():
    '''查询地址'''
    area_list = Area.query.all()
    area_dict_list = [area.to_dict() for area in area_list]
    '''查询设施'''
    facility_list = Facility.query.all()
    facility_dict_list = [facility.to_dict() for facility in facility_list]
    '''构造结果并返回'''
    return jsonify(code='200',area=area_dict_list, facility=facility_dict_list)


@house_blue.route('/detail/', methods=['GET'])
def detail():
    if request.method == 'GET':
        return render_template('detail.html')


@house_blue.route('/detail/<int:id>/', methods=['GET'])
def house_detail(id):
    if request.method == 'GET':
        '''通过房屋的id查询到该房屋对象'''
        house = House.query.get(id)
        '''查询房屋的设施信息,通过house.facilities查询到的是该房屋的所有设施的对象列表'''
        facility_list = house.facilities
        facility_dict_list = [facility.to_dict() for facility in facility_list]
        '''判断当前房屋信息是否为当前登录的用户发布，如果是则不显示预订按钮，如果house.user_id和session['user_id']相等，则该房屋为当前登录用户所发布'''
        booking = 1
        if 'user_id' in session:
            if house.user_id == session['user_id']:
                booking = 0
        '''返回房屋的所有信息，返回房屋的所有设备信息，显示预定状态'''
        return jsonify(house=house.to_full_dict(), facility_list=facility_dict_list, booking=booking)


'''房间预约，在首页点击图片可以跳转到房屋的详细信息的页面，在房屋的详细信息的页面，如果不是自己发布的房源，可以点击预约'''
@house_blue.route('/booking/', methods=['GET'])
def booking():
    if request.method == 'GET':
        if not session.get('user_id'):
            return redirect(url_for('user_blue.login'))
        return render_template('booking.html')


'''房间预约,房屋详细信息获取,这个主要是返回当前房屋的详细信息，所以根据房屋的id只能找到一个房屋，所以也只有一个详细信息可以返回'''
@house_blue.route('/get_booking_by_id/<int:id>/', methods=['GET'])
def get_booking_by_id(id):
    house = House.query.get(id)
    return jsonify(house=house.to_dict())



'''向用户展示我的房源的页面，在页面加载完成的时候，会向后端发送一个ajax请求，获取房源的数据'''
@house_blue.route('/my_house/', methods=['GET', 'POST'])
def my_house():
    if request.method == 'GET':
        return render_template('myhouse.html')


'''处理后端发送的ajax请求，返回后端需要的数据'''
@house_blue.route('/my_auth/', methods=['GET'])
def my_auth():
    '''验证当前用户是否完成实名认证'''
    '''获取当前登录用户的id'''
    user_id = session['user_id']
    '''获取当前用户对象'''
    user = User.query.get(user_id)
    if user.id_name:
        '''已经完成了实名认证，则查询该用户下面有几套房子'''
        # 分页
        page = request.args.get('page')
        if not page:
            page = 1
        else:
            page = int(page)
        house_list_paginate = House.query.filter_by(user_id=user_id).order_by(House.id.desc()).paginate(page, 10)
        house_list2 = []
        for house in house_list_paginate.items:
            house_list2.append(house.to_dict())

        # 获取页码列表
        # pages_iter = []
        # for item in house_list_paginate.iter_pages():
        #     pages_iter.append(item)
        if house_list_paginate.pages < 8:
            pages_iter = range(1,house_list_paginate.pages+1)
        else:
            if page <= 3:
                pages_iter = range(1,8)
            elif page >= house_list_paginate.pages - 2:
                pages_iter = range(house_list_paginate.pages - 5, house_list_paginate.pages+1)
            else:
                pages_iter = range(page - 3,page + 4)
        return jsonify(code='200', hlist=house_list2,paginate_pages=house_list_paginate.pages, paginate_page=house_list_paginate.page, iter_pages = list(pages_iter))
    else:
        '''没有完成实名认证'''
        return jsonify(status_code.MYHOUSE_USER_IS_NOT_AUTH)


@house_blue.route('/new_house/', methods=['GET', 'POST'])
def new_house():
    if request.method == 'GET':
        return render_template('newhouse.html')

    if request.method == 'POST':
        # 房屋主人的用户编号
        user_id = session.get('user_id')
        # 归属地的区域编号
        area_id = request.form.get('area_id')
        # 房屋标题
        title = request.form.get('title')
        # 单价 单位：元
        price = request.form.get('price')
        # 房屋地址
        address = request.form.get('address')
        # 房间数目
        room_count = request.form.get('room_count')
        # 房屋面积
        acreage = request.form.get('acreage')
        # 房屋类型 如：几室几厅
        unit = request.form.get('unit')
        # 房屋容纳的人数
        capacity = request.form.get('capacity')
        # 房屋床铺配置
        beds = request.form.get('beds')
        # 房屋押金
        deposit = request.form.get('deposit')
        # 最低入住天数
        min_days = request.form.get('min_days')
        # 最多入住天数， 0表示不受限制
        max_days = request.form.get('max_days')
        facilities = request.form.getlist('facility')
        front_img = request.files.get('house_image')
        detail_imgs = request.files.getlist('house_detail_image')
        # 验证数据完整性
        if not all([area_id, title, price, address, room_count, acreage, unit, capacity, beds, deposit, min_days, facilities]):
            return jsonify(status_code.PARAMS_ERROR)
        # 验证图片数据格式
        for item in detail_imgs+[front_img]:
            allow_suffix = ['jpg', 'png', 'jpeg', 'gif', 'bmp']
            file_suffix = item.filename.split(".")[-1]
            if file_suffix not in allow_suffix:
                return jsonify({"error": 1, "message": "图片格式不正确"})
        # 创建房间
        house = House()
        house.user_id = user_id
        house.area_id = area_id
        house.title = title
        house.price = price
        house.address = address
        house.room_count = room_count
        house.acreage = acreage
        house.unit = unit
        house.capacity = capacity
        house.beds = beds
        house.deposit = deposit
        house.min_days = min_days
        house.max_days = max_days
        house.order_count = 0
        # 存储首图
        if not os.path.exists(r'./static/upload/house/'+str(house.user_id)):
            os.mkdir( r'./static/upload/house/'+str(house.user_id))
        path = r'./static/upload/house/'+str(house.user_id)+'/'+house.title+'_front.'+front_img.filename.split(".")[-1]
        front_img.save(path)
        house.index_image_url = path[1:]
        house.save()

        # 获取房间id
        house_id = House.query.order_by(House.id.desc()).first().id
        # 存储房间设施
        for facility in facilities:
            item = Facility.query.filter_by(id=facility).first()
            house.facilities.append(item)
        house.save()

        # 存储房间图片
        for i in range(len(detail_imgs)):
            path = r'./static/upload/house/'+str(house.user_id)+'/'+house.title+'_'+str(i) + '.'+ detail_imgs[i].filename.split(".")[-1]
            detail_imgs[i].save(path)
            item = HouseImage()
            item.house_id = house_id
            item.url = path[1:]
            item.save()
        return jsonify(status_code.SUCCESS)
