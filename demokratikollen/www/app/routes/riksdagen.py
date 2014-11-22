# Import flask dependencies
from flask import Blueprint, request, jsonify, render_template

#import the relevant controllers
#from demokratikollen.www.app.controllers import riksdagen
from demokratikollen.www.app.helpers.db import db
from demokratikollen.www.app.helpers.cache import cache

# Define the blueprint: 'auth', set its url prefix: app.url/auth
riksdagen_blueprint = Blueprint('riksdagen', __name__, url_prefix='/riksdagen')

# Set the route and accepted methods
@riksdagen_blueprint.route('/', methods=['GET'])
def index():
   return render_template('riksdagen/index.html')