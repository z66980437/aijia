from aj_app.views.house_views import house_blue
from aj_app.views.index_views import index_blue
from aj_app.views.order_views import order_blue
from aj_app.views.user_views import user_blue


def init_blue(app):
    app.register_blueprint(blueprint=house_blue)
    app.register_blueprint(blueprint=index_blue)
    app.register_blueprint(blueprint=order_blue)
    app.register_blueprint(blueprint=user_blue)


