from flask import Blueprint, render_template, redirect, url_for
from flask.ext.wtf import Form, RecaptchaField
from flask.ext.wtf.file import FileField, FileAllowed, FileRequired
from os import listdir
from os.path import isfile, join
from werkzeug.utils import secure_filename
from wtforms import HiddenField, SubmitField
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
    recaptcha = RecaptchaField()
    submit = SubmitField('Upload')


class RemoveForm(Form):
    filename = HiddenField('Schematic to delete')
    submit = SubmitField('Delete')


@blueprint.route('/')
def index():
    path = blueprint.config.get('SCHEMATICS_PATH')
    os.chdir(path)

    upload_form = UploadForm()
    remove_form = RemoveForm()

    files = filter(os.path.isfile, os.listdir(path))
    files.sort(key=os.path.getmtime, reverse=True)
    return render_template('schematics/index.html', files=files, upload_form=upload_form, remove_form=remove_form)


@blueprint.route('/upload', methods=['POST'])
def upload():
    path = blueprint.config.get('SCHEMATICS_PATH')
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.schematic.data.filename)
        form.schematic.data.save(path + filename)
    return redirect(url_for('.index'))


@blueprint.route('/remove', methods=['POST'])
def remove():
    path = blueprint.config.get('SCHEMATICS_PATH')
    form = RemoveForm()
    files = [f for f in listdir(path) if isfile(join(path, f))]

    filename = form.filename.data
    if filename not in files:
        return redirect(url_for('.index'))

    os.renames(path + filename, path + 'deleted/' + filename)
    return redirect(url_for('.index'))
