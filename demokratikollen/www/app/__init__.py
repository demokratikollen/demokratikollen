# Import flask and template operators
from flask import Flask, render_template
import os

#import helpers
from demokratikollen.www.app.helpers.cache import cache
from demokratikollen.www.app.helpers.db import db

import demokratikollen.www.app.views.data.member
import demokratikollen.www.app.views.data.parliament
import demokratikollen.www.app.views.pages
from demokratikollen.www.app import views


#App Factory to facilitate testing.
def create_app(testing=False, caching=True):
    app = Flask(__name__, static_url_path='', static_folder='static')

    #Load the basic config.
    app.config.from_object('demokratikollen.www.config')

    #If we require testing. change some configs.
    if testing:
        print("Running Test env.")
        app.config['TESTING'] = True
        cache.config['CACHE_TYPE'] = 'null'

    if not caching:
        cache.config['CACHE_TYPE'] = 'null'

    #init the cache
    cache.init_app(app)

    #inti the db
    db.init_app(app)

    # 404 error handling
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    # Import a module / component using its blueprint handler variable

    blueprints = (
        views.data.parliament.blueprint,
        views.data.member.blueprint,
        views.pages.blueprint)

    # Register blueprint(s)
    for b in blueprints:
        app.register_blueprint(b)

    return app








