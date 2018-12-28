from datetime import datetime

from flask import Blueprint, jsonify, session, request, render_template

from aj_app.models import Order, House
from utils import status_code

order_blue = Blueprint('order_blue', __name__, url_prefix='/order/')

@order_blue.route('/create/', methods=['POST'])
def create():
    # 接收参数
    dict = request.form
    house_id = int(dict.get('house_id'))
    '''将日期字符串转化成datatime对象'''
    start_date = datetime.strptime(dict.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(dict.get('end_date'), '%Y-%m-%d')
    '''验证数据的完整性'''
    if not all([house_id, start_date, end_date]):
        return jsonify(status_code.PARAMS_ERROR)
    if start_date > end_date:
        return jsonify(status_code.ORDER_START_END_TIME_ERROR)
    '''查询房屋对象'''
    try:
        '''根据房屋的id去查询房屋的对象'''
        house = House.query.get(house_id)
    except:
        return jsonify(status_code.DATABASE_ERROR)
    '''创建订单'''
    order = Order()
    order.user_id = session['user_id']
    order.house_id = house_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = (end_date - start_date).days + 1
    order.house_price = house.price
    order.amount = order.days * order.house_price
    '''调用对象方法去创建一个订单对象'''
    try:
        order.add_update()
        '''房屋订单数加一'''
        house.order_count += 1
        house.save()
    except:
        return jsonify(status_code.DATABASE_ERROR)

    '''返回信息'''
    return jsonify(code=status_code.OK)


'''
个人订单，返回自己所下过的订单的页面
'''
@order_blue.route('/my_order/', methods=['GET'])
def my_order():
    if request.method == 'GET':
        return render_template('order.html')


'''
所有订单接口,作为租客查询自己的订单
'''
@order_blue.route('/all_order/', methods=['GET'])
def all_order():
    '''找到用户的id'''
    uid = session['user_id']
    '''根据用户的id和订单的关联关系，找到所有的订单'''
    order_list = Order.query.filter(Order.user_id == uid).order_by(Order.id.desc())
    order_list2 = [order.to_dict() for order in order_list]
    return jsonify(olist=order_list2)


'''
作为房东可以查询别人对自己发布的房子所下的订单
'''
@order_blue.route('/orders/', methods=['GET'])
def orders():
    if request.method == 'GET':
        return render_template('orders.html')


'''
作为房东查询订单
'''
@order_blue.route('/fd/',methods=['GET'])
def find_orders():
    '''查询登录用户的id'''
    uid=session['user_id']
    '''查询当前用户名下所有的房子，并且返回房子的id构成的列表'''
    hlist=House.query.filter(House.user_id==uid)
    hid_list=[house.id for house in hlist]
    '''根据房子的id查询房屋的订单'''
    order_list=Order.query.filter(Order.house_id.in_(hid_list)).order_by(Order.id.desc())
    '''构造出需要返回的结果'''
    olist=[order.to_dict() for order in order_list]
    return jsonify(olist=olist)


@order_blue.route('/orders/<int:id>/', methods=['PUT'])
def change_orders(id):
    if request.method == 'PUT':
        status = request.form.get('status')
        order = Order.query.filter(Order.id==id).first()
        # 接单
        if status == 'WAIT_PAYMENT':
            order.status = 'WAIT_PAYMENT'
            order.save()
            return jsonify(status_code.SUCCESS)
        # 拒单
        elif status == 'REJECTED':
            comment = request.form.get('comment')
            order.status = 'REJECTED'
            order.comment = comment
            order.save()
            return jsonify(status_code.SUCCESS)
        # status有误
        else:
            return jsonify(status_code.ORDERS_STATUS_ERROR)
