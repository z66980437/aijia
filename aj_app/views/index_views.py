from flask import Blueprint, render_template, redirect

from aj_app.models import Area

index_blue = Blueprint('index_blue', __name__)

@index_blue.route('/')
def my_index():
    return redirect('/house/index/')