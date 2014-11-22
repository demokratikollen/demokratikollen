from flask import Blueprint, request
from demokratikollen.www.app.models import data

from datetime import date

blueprint = Blueprint('data', __name__, url_prefix='/data')

# Set the route and accepted methods
@blueprint.route('/gender.json', methods=['GET'])
def gender_json():
    str_date = request.args.get('date', '')
    party = request.args.get('party','')
    
    #Check if the party exists
    if party and party not in get_parties():
        msg = "Partiförkortningen existerar ej. Möjliga är: <br>"
        for p in get_parties():
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

@cache.cached(3600*24)
def get_parties():
    return [r[0] for r in db.session.query(Party.abbr).all()]
