# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
from demokratikollen.www.app import db
from demokratikollen.www.app.helpers.cache import cache

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_static = Blueprint('static', __name__, url_prefix='/')

# Set the route and accepted methods
@mod_static.route('/', methods=['GET'])
@cache.cached()
def index():
    return render_template("/static/index.html", header_home_class = 'active')

@mod_static.route('kontakt')
def contact():
	return render_template("/static/contact.html")