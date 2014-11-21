from datetime import date
from flask import Blueprint, request
from demokratikollen.www.app.controllers import simple

# Define the blueprint: 'auth', set its url prefix: app.url/auth
basic_blueprint = Blueprint('basic', __name__)

# Set the route and accepted methods
@basic_blueprint.route('/', methods=['GET'])
def index():
    return simple.index()

@basic_blueprint.route('/riksdagen', methods=['GET'])
def parliament():
    return simple.parliament()

@basic_blueprint.route('/partierna', methods=['GET'])
def parties():
    return simple.parties()

@basic_blueprint.route('/forslagen', methods=['GET'])
def issues():
    return simple.issues()

@basic_blueprint.route('/om', methods=['GET'])
def about():
    return simple.about()