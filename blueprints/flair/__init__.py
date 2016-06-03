from flask import Blueprint, render_template, request, session, redirect, url_for
import hashlib
import os
import praw
import urllib

from blueprints.id import mc_auth

blueprint = Blueprint('flair', __name__, url_prefix='/flair')
blueprint.config = {}

bot = None
oauth = None


@blueprint.record
def record_config(setup_state):
    app = setup_state.app
    blueprint.config = dict([(key, value) for (key, value) in app.config.iteritems()])

    global bot
    bot = praw.Reddit(
        'script:bromweb.flair.mod:v1.0 (by /u/williammck)',
        oauth_client_id=blueprint.config.get('REDDIT_BOT_CLIENT_ID'),
        oauth_client_secret=blueprint.config.get('REDDIT_BOT_CLIENT_SECRET'),
        oauth_redirect_uri='http://www.example.com/unused/redirect/uri',
        oauth_grant_type='password',
        user=blueprint.config.get('REDDIT_BOT_USERNAME'),
        pswd=blueprint.config.get('REDDIT_BOT_PASSWORD'),
    )

    global oauth
    oauth = praw.Reddit(
        'web:bromweb.flair.client:v1.0 (by /u/williammck)',
        oauth_client_id=blueprint.config.get('REDDIT_CLIENT_ID'),
        oauth_client_secret=blueprint.config.get('REDDIT_CLIENT_SECRET'),
        oauth_redirect_uri=blueprint.config.get('REDDIT_REDIRECT_URI')
    )


@blueprint.route('/')
def index():
    state = hashlib.md5(os.urandom(24)).hexdigest()
    url = oauth.get_authorize_url(state, 'identity')
    return render_template('flair/index.html', url=url)


@blueprint.route('/callback')
def callback():
    code = request.args.get('code', '')

    oauth.get_access_information(code)
    reddit_username = oauth.get_me().name

    session['reddit_username'] = reddit_username

    return redirect(url_for('.menu'))


@blueprint.route('/menu')
def menu():
    if 'reddit_username' not in session:
        return redirect(url_for('.index'))

    return render_template('flair/menu.html')


@blueprint.route('/auth')
def auth():
    return mc_auth(url_for('.confirm'))


@blueprint.route('/confirm')
def confirm():
    if 'reddit_username' not in session:
        return redirect(url_for('index'))
    if 'minecraft_username' not in session:
        return redirect(url_for('minecraft_auth'))

    reddit_username = session['reddit_username']
    minecraft_username = session['minecraft_username']

    if reddit_username.lower() == minecraft_username.lower():
        same_username = True
    else:
        same_username = False

    return render_template('flair/confirm.html', same_username=same_username)


@blueprint.route('/retry')
def retry():
    session.clear()
    return redirect(url_for('.index'))


@blueprint.route('/submit')
def submit():
    if 'reddit_username' not in session:
        return redirect(url_for('.index'))
    if 'minecraft_username' not in session:
        return redirect(url_for('.auth'))

    reddit_username = session['reddit_username']
    minecraft_uuid = session['minecraft_uuid']
    minecraft_username = session['minecraft_username']

    bot.get_access_information(None)

    minecraft_head_url = 'https://crafatar.com/avatars/' + minecraft_uuid + '?size=32'
    minecraft_head_path, headers = urllib.urlretrieve(minecraft_head_url)
    bot.upload_image(blueprint.config.get('REDDIT_SUBREDDIT'), minecraft_head_path, minecraft_username)

    flair_css = ".flair-" + minecraft_username + "{ background: url(%%" + minecraft_username + "%%); }\n"
    stylesheet = bot.get_stylesheet(blueprint.config.get('REDDIT_SUBREDDIT'))['stylesheet']
    if flair_css not in stylesheet:
        stylesheet = stylesheet.replace(
            blueprint.config.get('REDDIT_CSS_MARKER'),
            flair_css + blueprint.config.get('REDDIT_CSS_MARKER')
        )
        bot.set_stylesheet(blueprint.config.get('REDDIT_SUBREDDIT'), stylesheet)

    if reddit_username.lower() == minecraft_username.lower():
        flair_text = ''
    else:
        flair_text = minecraft_username

    bot.set_flair(blueprint.config.get('REDDIT_SUBREDDIT'), reddit_username, flair_text, minecraft_username)
    return redirect(url_for('.done'))


@blueprint.route('/remove')
def remove():
    if 'reddit_username' not in session:
        return redirect(url_for('.index'))

    reddit_username = session['reddit_username']

    bot.get_access_information(None)
    bot.set_flair(blueprint.config.get('REDDIT_SUBREDDIT'), reddit_username)

    return redirect(url_for('.done'))


@blueprint.route('/done')
def done():
    if 'reddit_username' not in session:
        return redirect(url_for('.index'))

    session.clear()
    return render_template('flair/done.html')
