from flask import Blueprint, request, jsonify
from demokratikollen.www.app.models import parliament

import datetime

blueprint = Blueprint('parliament', __name__, url_prefix='/data/parliament')

# Set the route and accepted methods
@blueprint.route('/gender.json', methods=['GET'])
def gender_json():
    str_date = request.args.get('date', '')
    party = request.args.get('party','')
    
    #Check if the party exists
    parties = parliament.get_parties()
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
            return "Felaktig datumparameter. Formatet är: ÅÅÅÅ-MM-DD", 400

    json = parliament.gender(date=date,party=party)

    return jsonify(json)

# Set the route and accepted methods
@blueprint.route('/parliament.json', methods=['GET'])
def parliament_json():
    str_date = request.args.get('date', '')

    # Check if the date supplied is ok.
    if not str_date:
        date = datetime.date.today()
    else:
        try:
            date = datetime.datetime.strptime(str_date, '%Y-%m-%d').date()
        except ValueError:
            return "Felaktig datumparameter. Formatet är: ÅÅ-MM-DD", 400

    json = parliament.parliament(date=date)

    return jsonify(json)

@blueprint.route('/appointments.json', methods=['GET'])
def appointments_json():
    json = """
    [
        { "x": 0, "y": 0 },
        { "x": 100.5, "y": 0.95 },
        { "x": 0.5, "y": 0.95 }
    ]"""

    json = """
    [
        [0,0],
        [100,50],
        [100,100]
    ]
    """

    return json
