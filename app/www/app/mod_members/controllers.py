# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  json

# Import the database object from the main app module
from app import db

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_members = Blueprint('members', __name__, url_prefix='/members')

# Set the route and accepted methods
@mod_members.route('/', methods=['GET'])
def member():
    return render_template("/members/members.html",
                            header_members_class="active")

@mod_members.route('/<int:member_id>.<string:format>', methods=['GET'])
def get_member(member_id,format):
    VALID_FORMATS = ['json']
    if not format in VALID_FORMATS:
        raise ValueError('Format not recognized.')
    member = {
                "name": "Test T. Testsson",
                "attendance": [0.8,0.7,0.6,0.8,1.0],
                "id": member_id
            }
    return json.jsonify(member)

