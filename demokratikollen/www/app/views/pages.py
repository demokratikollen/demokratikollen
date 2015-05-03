# -*- coding: utf-8 -*-

from datetime import datetime

# Import flask dependencies
from flask import request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
from demokratikollen.www.app.helpers.cache import cache, http_expires
from demokratikollen.www.app.helpers.db import db
from demokratikollen.core.db_structure import Member, ChamberAppointment, Party
from demokratikollen.www.app.models.proposals import proposals_main
from demokratikollen.www.app.models.sitemap import sitemap_pages
from flask import Blueprint, request, jsonify, Markup
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from demokratikollen.core.utils.mongodb import MongoDBDatastore


blueprint = Blueprint('pages', __name__)

def render_parliament():
    return render_template("/parliament/index.html")

# Set the route and accepted methods
@blueprint.route('/', methods=['GET'])
def index():
    return render_parliament()

@blueprint.route('/riksdagen', methods=['GET'])
def parliament():
    return render_parliament()

@blueprint.route('/partierna', methods=['GET'])
def parties():
    return render_template("/parties/index.html")

@blueprint.route('/forslagen/<string:gov>', methods=['GET'])
def proposals(gov):

    try:
        proposals_main_data = proposals_main(gov)
    except KeyError:
        return render_template('404.html'), 404

    return render_template("/proposals/index.html",
                                data = proposals_main_data
                               )

@blueprint.route('/om', methods=['GET'])
def about():
    return render_template("/about.html")

@blueprint.route("/sitemap.xml")
def sitemap():
    pages = sitemap_pages()
    return render_template("/sitemap.xml", pages=pages)

@blueprint.route("/sekretesspolicy.html")
def privacypolicy():
    return render_template("/privacypolicy.html")

@blueprint.route('/search.json', methods=['GET'])
@http_expires(3600*24)
@cache.cached(3600*24)
def timeseries():
    ds = MongoDBDatastore()
    return jsonify(ds.get_object("search"))

def render_party(p):
    return render_template("/parties/party.html",party=p)
def render_member(m):
    return render_template("/parliament/member.html", member=m)

@blueprint.route('/<arg>', methods=['GET'])
def missing(arg):
    # first try party abbreviations
    try:
        p = db.session.query(Party).filter(func.lower(Party.abbr)==arg.lower()).one()
        return render_party(p)
    except NoResultFound as e:
        pass        

    # try party full name
    try:
        p = db.session.query(Party).filter(func.lower(Party.name)==arg.lower()).one()
        return render_party(p)
    except NoResultFound as e:
        pass

    # try member url_name
    try:
        m = db.session.query(Member).filter(Member.url_name==arg.lower()).one()
        return render_member(m)
    except NoResultFound as e:
        pass

    return render_template('404.html'), 404



