from flask import Blueprint, render_template

blueprint = Blueprint('standalone', __name__, url_prefix='/')


@blueprint.route('/')
def index():
    return render_template('standalone/index.html')
