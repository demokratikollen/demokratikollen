# -*- coding: utf-8 -*-

# Import flask dependencies
from flask import request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
from demokratikollen.www.app.helpers.cache import cache
from demokratikollen.www.app.helpers.db import db
from demokratikollen.core.db_structure import Member, ChamberAppointment, Party
from demokratikollen.www.app.models.parties import party_bias
from flask import Blueprint, request
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

blueprint = Blueprint('pages', __name__)

# Set the route and accepted methods
@blueprint.route('/', methods=['GET'])
def index():
    return render_template("/index.html")

@blueprint.route('/riksdagen/', methods=['GET'])
def parliament():
    return render_template("/parliament/index.html")

@blueprint.route('/partierna', methods=['GET'])
def parties():

    party_bias_data = party_bias("S","M")

    return render_template("/parties/index.html",
                            party_bias_parties = party_bias_data["parties"],
                            party_bias_yticklabels = party_bias_data["yticklabels"])

@blueprint.route('/forslagen', methods=['GET'])
def proposals():
    return render_template("/proposals/index.html")

@blueprint.route('/om', methods=['GET'])
def about():
    return render_template("/about.html")

@blueprint.route('/partierna/<abbr>.html', methods=['GET'])
def party(abbr):
    try:
        p = db.session.query(Party).filter(func.lower(Party.abbr)==abbr.lower()).one()
    except NoResultFound as e:
        return render_template('404.html'), 404
    return render_template("/parties/party.html",party=p)