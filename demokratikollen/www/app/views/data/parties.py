from flask import Blueprint, request, jsonify, render_template
# from demokratikollen.www.app.models import parties
from demokratikollen.www.app.models.parties import party_election, get_municipality_timeseries

import datetime

blueprint = Blueprint('elections', __name__, url_prefix='/data/elections')

@blueprint.route('/<int:year>/<abbr>.json')
def election(year,abbr):
    try:
        d = party_election(abbr,year)
    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)

@blueprint.route('/timeseries/<abbr>/<int:municipality_id>.json')
def municipality_timeseries(abbr,municipality_id):
    try:
        d = get_municipality_timeseries(abbr,municipality_id)
    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)