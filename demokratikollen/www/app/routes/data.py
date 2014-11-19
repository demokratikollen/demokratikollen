# Import flask dependencies
from flask import Blueprint

#import the relevant controllers
from demokratikollen.www.app.controllers import data

# Define the blueprint: 'auth', set its url prefix: app.url/auth
data_blueprint = Blueprint('data', __name__, url_prefix='/data')

# Set the route and accepted methods
@data_blueprint.route('/gender.json', methods=['GET'])
def index():
    return data.gender_json()