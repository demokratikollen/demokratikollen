# Import flask and template operators
from flask import Flask, render_template

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

import sys
import os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from db_structure import *

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_static.controllers import mod_static as static_module
from app.mod_members.controllers import mod_members as members_module

# Register blueprint(s)
app.register_blueprint(static_module)
app.register_blueprint(members_module)
# app.register_blueprint(xyz_module)
# ..
