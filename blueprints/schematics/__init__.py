from flask import Blueprint, render_template, request, session, redirect, url_for
from os import listdir
from os.path import isfile, join

blueprint = Blueprint('schematics', __name__, url_prefix='/schematics')
blueprint.config = {}


@blueprint.record
def record_config(setup_state):
    app = setup_state.app
    blueprint.config = dict([(key, value) for (key, value) in app.config.iteritems()])


@blueprint.route('/')
def index():
    path = blueprint.config.get('SCHEMATICS_PATH')
    files = [f for f in listdir(path) if isfile(join(path, f))]
    return render_template('schematics/index.html', files=files)
