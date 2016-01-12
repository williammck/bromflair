from flask import Flask, render_template, request, session, redirect, url_for
import config
import hashlib
import jwt
import os
import praw
import urllib

app = Flask(__name__)
app.config.from_object(config)

SECRET_KEY = app.config.get('SECRET_KEY')
JWT_SECRET = app.config.get('JWT_SECRET')
REDDIT_CLIENT_ID = app.config.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = app.config.get('REDDIT_CLIENT_SECRET')
REDDIT_REDIRECT_URI = app.config.get('REDDIT_REDIRECT_URI')
REDDIT_BOT_USERNAME = app.config.get('REDDIT_BOT_USERNAME')
REDDIT_BOT_PASSWORD = app.config.get('REDDIT_BOT_PASSWORD')
REDDIT_SUBREDDIT = app.config.get('REDDIT_SUBREDDIT')
REDDIT_CSS_MARKER = app.config.get('REDDIT_CSS_MARKER')

bot = praw.Reddit('BromFlair v1.0 by williammck')
bot.config.decode_html_entities = True
oauth = praw.Reddit('BromFlair v1.0 OAuth by williammck')
oauth.set_oauth_app_info(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REDIRECT_URI)


@app.route('/')
def index():
    state = hashlib.md5(os.urandom(24)).hexdigest()
    url = oauth.get_authorize_url(state, 'identity')
    return render_template('index.html', url=url)

@app.route('/reddit/callback')
def reddit_callback():
    code = request.args.get('code', '')

    oauth.get_access_information(code)
    reddit_username = oauth.get_me().name

    session['reddit_username'] = reddit_username

    return redirect(url_for('menu'))

@app.route('/menu')
def menu():
    if 'reddit_username' not in session:
        return redirect(url_for('index'))

    return render_template('menu.html')

@app.route('/minecraft/auth')
def minecraft_auth():
    if 'reddit_username' not in session:
        return redirect(url_for('index'))

    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For']
    else:
        ip = request.remote_addr

    return render_template('minecraft_auth.html', ip=ip)

@app.route('/minecraft/callback')
def minecraft_callback():
    if 'reddit_username' not in session:
        return redirect(url_for('index'))

    data = request.args.get('data', '')
    minecraft = jwt.decode(data, JWT_SECRET, algorithms=['HS256'])

    minecraft_uuid = minecraft['uuid']
    minecraft_username = minecraft['username']
    minecraft_ip = minecraft['ip']

    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For']
    else:
        ip = request.remote_addr

    if minecraft_ip != ip:
        error = 'IP Address differs.'
        return render_template('error.html', error=error)

    session['minecraft_uuid'] = minecraft_uuid
    session['minecraft_username'] = minecraft_username
    session['minecraft_ip'] = minecraft_ip

    return redirect(url_for('flair_confirm'))

@app.route('/flair/confirm')
def flair_confirm():
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

    return render_template('flair_confirm.html', same_username=same_username)

@app.route('/flair/retry')
def flair_retry():
    session.clear()
    return redirect(url_for('index'))

@app.route('/flair/submit')
def flair_submit():
    if 'reddit_username' not in session:
        return redirect(url_for('index'))
    if 'minecraft_username' not in session:
        return redirect(url_for('minecraft_auth'))

    bot.login(REDDIT_BOT_USERNAME, REDDIT_BOT_PASSWORD, disable_warning=True)

    reddit_username = session['reddit_username']
    minecraft_uuid = session['minecraft_uuid']
    minecraft_username = session['minecraft_username']

    minecraft_head_url = 'https://crafatar.com/avatars/' + minecraft_uuid + '?size=32'
    minecraft_head_path, headers = urllib.urlretrieve(minecraft_head_url)
    bot.upload_image(REDDIT_SUBREDDIT, minecraft_head_path, minecraft_username)

    flair_css = ".flair-" + minecraft_username + "{ background: url(%%" + minecraft_username + "%%); }\n"
    stylesheet = bot.get_stylesheet(REDDIT_SUBREDDIT)['stylesheet']
    if flair_css not in stylesheet:
        stylesheet = stylesheet.replace(REDDIT_CSS_MARKER, flair_css + REDDIT_CSS_MARKER)
        bot.set_stylesheet(REDDIT_SUBREDDIT, stylesheet)

    if reddit_username.lower() == minecraft_username.lower():
        flair_text = ''
    else:
        flair_text = minecraft_username

    bot.set_flair(REDDIT_SUBREDDIT, reddit_username, flair_text, minecraft_username)
    return redirect(url_for('done'))

@app.route('/flair/remove')
def flair_remove():
    if 'reddit_username' not in session:
        return redirect(url_for('index'))

    bot.login(REDDIT_BOT_USERNAME, REDDIT_BOT_PASSWORD, disable_warning=True)

    reddit_username = session['reddit_username']
    bot.set_flair(REDDIT_SUBREDDIT, reddit_username)
    return redirect(url_for('done'))

@app.route('/done')
def done():
    if 'reddit_username' not in session:
        return redirect(url_for('index'))

    session.clear()
    return render_template('done.html')


if __name__ == '__main__':
    app.run(debug=True)
