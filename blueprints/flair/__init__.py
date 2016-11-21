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
        user_agent='script:bromweb.flair.mod:v1.0 (by /u/williammck)',
        client_id=blueprint.config.get('REDDIT_BOT_CLIENT_ID'),
        client_secret=blueprint.config.get('REDDIT_BOT_CLIENT_SECRET'),
        username=blueprint.config.get('REDDIT_BOT_USERNAME'),
        password=blueprint.config.get('REDDIT_BOT_PASSWORD'),
    )

    global oauth
    oauth = praw.Reddit(
        user_agent='web:bromweb.flair.client:v1.0 (by /u/williammck)',
        client_id=blueprint.config.get('REDDIT_CLIENT_ID'),
        client_secret=blueprint.config.get('REDDIT_CLIENT_SECRET'),
        redirect_uri=blueprint.config.get('REDDIT_REDIRECT_URI')
    )


@blueprint.route('/')
def index():
    state = hashlib.md5(os.urandom(24)).hexdigest()
    url = oauth.auth.url(['identity'], state, 'temporary')
    return render_template('flair/index.html', url=url)


@blueprint.route('/callback')
def callback():
    if 'error' in request.args:
        return redirect(url_for('.index'))

    code = request.args.get('code')

    oauth.auth.authorize(code)

    reddit_username = oauth.user.me().name
    session['reddit_username'] = reddit_username

    oauth.read_only = True

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

    subreddit = bot.subreddit(blueprint.config.get('REDDIT_SUBREDDIT'))

    minecraft_head_url = 'https://crafatar.com/avatars/' + minecraft_uuid + '?size=32'
    minecraft_head_path, headers = urllib.urlretrieve(minecraft_head_url)
    subreddit.stylesheet.upload(minecraft_username, minecraft_head_path)

    flair_css = '.flair-' + minecraft_username + ' { background: url(%%' + minecraft_username + '%%) }\n'
    stylesheet = subreddit.stylesheet().stylesheet
    if flair_css not in stylesheet:
        stylesheet = stylesheet.replace(
            blueprint.config.get('REDDIT_CSS_MARKER'),
            flair_css + blueprint.config.get('REDDIT_CSS_MARKER')
        )
        subreddit.stylesheet.update(stylesheet, 'Added flair for ' + minecraft_username)

    if reddit_username.lower() == minecraft_username.lower():
        flair_text = ''
    else:
        flair_text = minecraft_username

    subreddit.flair.set(reddit_username, flair_text, minecraft_username)
    return redirect(url_for('.done'))


@blueprint.route('/remove')
def remove():
    if 'reddit_username' not in session:
        return redirect(url_for('.index'))

    reddit_username = session['reddit_username']

    subreddit = bot.subreddit(blueprint.config.get('REDDIT_SUBREDDIT'))
    subreddit.flair.delete(reddit_username)

    return redirect(url_for('.done'))


@blueprint.route('/done')
def done():
    if 'reddit_username' not in session:
        return redirect(url_for('.index'))

    session.clear()
    return render_template('flair/done.html')
