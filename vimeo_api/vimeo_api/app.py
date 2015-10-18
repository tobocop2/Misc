from flask import Flask, jsonify
from celery import Celery
from .config import DefaultConfig
from .api import api
from .extensions import db, migrate, cache
import os

DEFAULT_BLUEPRINTS = {api}


def create_app(config=None, app_name=None, blueprints=None):

    if app_name is None:
        app_name = DefaultConfig.PROJECT

    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(__name__)
    configure_app(app, os.environ['APP_SETTINGS'])
    configure_extensions(app)
    configure_blueprints(app, blueprints)
    configure_error_handlers(app)

    return app


def configure_app(app, config=None):
    app.config.from_object(os.environ['APP_SETTINGS'])

    if config:
        app.config.from_object(config)


def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)

    # flask-migrate
    migrate.init_app(app, db)

    # flask-cache
    cache.init_app(app)


def configure_blueprints(app, blueprints):
    # only one blueprint in this case, but
    # extensible for many
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_error_handlers(app):
    @app.errorhandler(400)
    @cache.cached(timeout=50, key_prefix='bad_request')
    def bad_request(error):
        return jsonify(error='Bad Request'), 400

    @app.errorhandler(401)
    @cache.cached(timeout=50, key_prefix='unauthorized')
    def unauthorized(error):
        return jsonify(error='Unauthorized'), 401

    @app.errorhandler(404)
    @cache.cached(timeout=50, key_prefix='not_found')
    def not_found(error):
        return jsonify(error='Not Found'), 404

    @app.errorhandler(405)
    @cache.cached(timeout=50, key_prefix='not_found')
    def method_not_allowed(error):
        return jsonify(error='Method not Allowed'), 405

    @app.errorhandler(410)
    @cache.cached(timeout=50, key_prefix='gone')
    def gone(error):
        return jsonify(error='Gone'), 410

    @app.errorhandler(413)
    @cache.cached(timeout=50, key_prefix='too_large')
    def request_entity_to_large(error):
        return jsonify(error='Request Entity too Large'), 413


def create_celery(app=None):
    app = app or create_app()
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
