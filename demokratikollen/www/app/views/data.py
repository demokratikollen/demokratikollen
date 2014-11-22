from flask import Blueprint, request
from demokratikollen.www.app.models import data

from datetime import date

blueprint = Blueprint('data', __name__, url_prefix='/data')

# Set the route and accepted methods
@blueprint.route('/gender.json', methods=['GET'])
def gender_json():
    a_date = request.args.get('date', date.today().isoformat())
    return data.gender_data(a_date)