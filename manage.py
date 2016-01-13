from flask.ext.script import Manager, Server
from app import application

manager = Manager(application)

manager.add_command("runserver", Server(host=application.config.get("HOST", "0.0.0.0"),
                                        port=application.config.get("PORT", 5000),
                                        use_evalex=application.config.get("DEBUG_SHELL")))


@manager.command
def print_routes():
    for rule in application.url_map.iter_rules():
        print rule, rule.endpoint

if __name__ == "__main__":
    manager.run()
