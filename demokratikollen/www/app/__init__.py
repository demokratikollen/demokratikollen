# Import flask and template operators
from flask import Flask, render_template

#import helpers
from demokratikollen.www.app.helpers.cache import cache
from demokratikollen.www.app.helpers.db import db

import os

#App Factory to facilitate testing.
def create_app(testing=False):
    app = Flask(__name__, static_url_path='', static_folder='static')

    #Load the basic config.
    app.config.from_object('demokratikollen.www.config')
    
    #If we require testing. change some configs.
    if testing:
        print("Running Test env.")
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['TEST_DATABASE_URL']
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
    from .routes import data

    # Register blueprint(s)
    app.register_blueprint(data.data_blueprint)

    return app








