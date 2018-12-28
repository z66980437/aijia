import os

from flask import Flask
from aj_app.ext import init_ext
from aj_app.settings import envs
from aj_app.views import init_blue

# 项目路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 静态文件
static_dir = os.path.join(BASE_DIR, 'static')
# 模板文件
template_dir = os.path.join(BASE_DIR, 'templates')

def create_app():
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    # 初始化app
    app.config.from_object(envs.get('develop'))
    # 初始化蓝图和路由
    init_blue(app)
    # 初始化第三方库
    init_ext(app)
    return app