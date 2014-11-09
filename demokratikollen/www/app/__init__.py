# Import flask and template operators
from flask import Flask, render_template

# Import extensions
from flask.ext.sqlalchemy import SQLAlchemy

#import the cache helper
from demokratikollen.www.app.helpers.cache import cache

#Import the orm.
from demokratikollen.core.db_structure import *

import os

def create_app(testing=False):
    # Define the WSGI application object
    app = Flask(__name__, static_url_path='/')
    # Configurations
    app.config.from_object('demokratikollen.www.config')

    if testing:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['TEST_DATABASE_URL']

    return app

def create_db(app):
    return SQLAlchemy(app)

def setup_app(app):    
    #init the cache
    cache.init_app(app)

    # 404 error handling
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    # Import a module / component using its blueprint handler variable
    from .mod_static.controllers import mod_static as static_module

    # Register blueprint(s)
    app.register_blueprint(static_module)

if 'TESTING' in os.environ:
    testing = True
else:
    testing = False

app = create_app(testing=testing)
db = create_db(app)
setup_app(app)






