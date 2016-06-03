import click
from flask import Flask
from flask_session import Session
from flask_wtf import CsrfProtect


def create_app(config_override=None):
    application = Flask(__name__)

    import config
    application.config.from_object(config)
    application.config.from_object(config_override)

    Session(application)
    CsrfProtect(application)

    from blueprints.api import api
    api.init_app(application)

    import blueprints
    for blueprint in blueprints.blueprints:
        application.register_blueprint(blueprint)

    @application.cli.command()
    def routes():
        for rule in application.url_map.iter_rules():
            click.echo("%s %s" % (rule, rule.endpoint))

    return application
