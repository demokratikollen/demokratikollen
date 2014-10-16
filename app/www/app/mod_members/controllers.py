# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  json

# Import the database object from the main app module
from app import db, Member

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_members = Blueprint('members', __name__, url_prefix='/members')

# Set the route and accepted methods
@mod_members.route('/', methods=['GET'])
def member():
    return render_template("/members/members.html",
                            header_members_class="active")

# Set the route and accepted methods
@mod_members.route('/<int:member_id>/absence', methods=['GET'])
def absence_graph(member_id):
    return render_template("/members/absence.html",member_id=member_id)

@mod_members.route('/<int:member_id>.<string:format>', methods=['GET'])
def get_member(member_id,format):
    VALID_FORMATS = ['json']
    if not format in VALID_FORMATS:
        raise ValueError('Format not recognized.')

    m = db.session.query(Member).filter_by(id=member_id).first()


    member = {
                "first_name": m.first_name,
                "last_name": m.last_name
            }
    return json.jsonify(member)

