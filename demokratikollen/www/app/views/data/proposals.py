from flask import Blueprint, request, jsonify, render_template
from flask.ext.jsontools import jsonapi
# from demokratikollen.www.app.models import parties
from demokratikollen.www.app.models.proposals import (
        party_detail,
        ministries_detail,
        members_detail,
        multiparties_detail
    )

from demokratikollen.www.app.helpers.db import db
from demokratikollen.www.app.helpers.cache import cache



import datetime
from demokratikollen.core.utils.mongodb import MongoDBDatastore

blueprint = Blueprint('proposals', __name__, url_prefix='/data')

@blueprint.route('/proposals/<string:gov>/party_detail_<int:party_id>.json')
def pd(gov,party_id):
    try:
        d = party_detail(gov,party_id)
    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)


@blueprint.route('/proposals/<string:gov>/ministries_detail.json')
def md(gov):
    try:
        d = ministries_detail(gov)

    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)


@blueprint.route('/proposals/<string:gov>/members_detail.json')
def md2(gov):
    try:
        d = members_detail(gov)

    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)


@blueprint.route('/proposals/<string:gov>/multiparties_detail.json')
def md3(gov):
    try:
        d = multiparties_detail(gov)

    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)

