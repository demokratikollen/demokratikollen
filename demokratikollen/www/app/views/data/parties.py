from flask import Blueprint, request, jsonify
# from demokratikollen.www.app.models import parties
from demokratikollen.www.app.models.parties import party_election

import datetime

blueprint = Blueprint('elections', __name__, url_prefix='/data/elections')

@blueprint.route('/<int:year>/<abbr>.json')
def election(year,abbr):
    d = party_election(abbr,year)
    return jsonify(d)