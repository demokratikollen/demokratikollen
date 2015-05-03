from flask import Blueprint, request, jsonify, render_template
from flask.ext.jsontools import jsonapi
# from demokratikollen.www.app.models import parties
from demokratikollen.www.app.models.proposals import (
        party_detail,
        ministries_detail,
        members_detail,
        multiparties_detail,
        committee_detail
    )

from demokratikollen.www.app.helpers.db import db
from demokratikollen.www.app.helpers.cache import cache, http_expires



import datetime
from demokratikollen.core.utils.mongodb import MongoDBDatastore

blueprint = Blueprint('proposals', __name__, url_prefix='/data')

@blueprint.route('/proposals/<string:gov>/party_detail_<int:party_id>.json')
@http_expires(3600*24)
@cache.memoize(3600*24)
def pd(gov,party_id):
    try:
        d = party_detail(gov,party_id)
    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)


@blueprint.route('/proposals/<string:gov>/ministries_detail.json')
@http_expires(3600*24)
@cache.memoize(3600*24)
def md(gov):
    try:
        d = ministries_detail(gov)

    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)


@blueprint.route('/proposals/<string:gov>/members_detail.json')
@http_expires(3600*24)
@cache.memoize(3600*24)
def md2(gov):
    print("ACTUALLY GETTING DATA")
    try:
        d = members_detail(gov)

    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)


@blueprint.route('/proposals/<string:gov>/multiparties_detail.json')
@http_expires(3600*24)
@cache.memoize(3600*24)
def md3(gov):
    try:
        d = multiparties_detail(gov)

    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)

@blueprint.route('/proposals/<string:gov>/committee_detail_<int:id>.json')
@http_expires(3600*24)
@cache.memoize(3600*24)
def cd(gov,id):
    try:
        d = committee_detail(gov,id)
    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)
