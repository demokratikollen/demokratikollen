# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_members = Blueprint('members', __name__, url_prefix='/members')

# Set the route and accepted methods
@mod_members.route('/', methods=['GET'])
def member():
    
    return render_template("/members/members.html", member=1)