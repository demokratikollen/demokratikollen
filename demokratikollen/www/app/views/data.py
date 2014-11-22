from flask import Blueprint, request, jsonify
from demokratikollen.www.app.models import data

import datetime

blueprint = Blueprint('data', __name__, url_prefix='/data')

# Set the route and accepted methods
@blueprint.route('/gender.json', methods=['GET'])
def gender_json():
    str_date = request.args.get('date', '')
    party = request.args.get('party','')
    
    #Check if the party exists
    parties = data.get_parties()
    if party and party not in parties:
        msg = "Partiförkortningen existerar ej. Möjliga är: <br>"
        for p in parties:
            msg = msg + p + "<br>"
        return msg, 400

    # Check if the date supplied is ok.
    if not str_date:
        date = datetime.date.today()
    else:
        try:
            date = datetime.datetime.strptime(str_date, '%Y-%m-%d').date()
        except ValueError:
            return "Felaktig datumparameter. Formatet är: ÅÅ-MM-DD", 400

    json = data.gender_json(date=date,party=party)

    return jsonify(json)