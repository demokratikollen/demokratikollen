# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db
from app import Member

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_static = Blueprint('static', __name__, url_prefix='/')

# Set the route and accepted methods
@mod_static.route('/', methods=['GET'])
def index():

    return render_template("/static/index.html", header_home_class = 'active')
