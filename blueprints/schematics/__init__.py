from flask import Blueprint, render_template, redirect, url_for
from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed, FileRequired
from os import listdir
from os.path import isfile, join
from werkzeug.utils import secure_filename
from wtforms import SubmitField
import os

blueprint = Blueprint('schematics', __name__, url_prefix='/schematics')
blueprint.config = {}


@blueprint.record
def record_config(setup_state):
    app = setup_state.app
    blueprint.config = dict([(key, value) for (key, value) in app.config.iteritems()])


class UploadForm(Form):
    schematic = FileField('Schematic to upload', validators=[
        FileRequired(),
        FileAllowed(['schematic'], 'Schematics only!')
    ])
    submit = SubmitField('Upload')


@blueprint.route('/')
def index():
    path = blueprint.config.get('SCHEMATICS_PATH')
    upload_form = UploadForm()
    files = [f for f in listdir(path) if isfile(join(path, f))]
    return render_template('schematics/index.html', files=files, upload_form=upload_form)


@blueprint.route('/upload', methods=['POST'])
def upload():
    path = blueprint.config.get('SCHEMATICS_PATH')
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.schematic.data.filename)
        form.schematic.data.save(path + filename)
    return redirect(url_for('.index'))


@blueprint.route('/remove/<filename>')
def remove(filename):
    path = blueprint.config.get('SCHEMATICS_PATH')
    files = [f for f in listdir(path) if isfile(join(path, f))]
    if filename not in files:
        return redirect(url_for('.index'))

    os.renames(path + filename, path + 'deleted/' + filename)
    return redirect(url_for('.index'))
