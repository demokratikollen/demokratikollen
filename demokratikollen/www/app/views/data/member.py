from flask import Blueprint, request, jsonify

blueprint = Blueprint('data', __name__, url_prefix='/data/member')

@blueprint.route('/appointments.json', methods=['GET'])
def appointments_json():
    json = """
    [
        { 
            "start": "2006-01-01T00:00:00",
            "end": "2010-01-01T00:00:00",
            "name": "Utskottet för det ena",
            "role": "Ordförande"
        },
        { 
            "start": "2003-01-01T00:00:00",
            "end": "2005-05-01T00:00:00",
            "name": "Utskottet för det ena",
            "role": "Suppleant"
        },
        { 
            "start": "2008-01-01T00:00:00",
            "end": "2012-01-01T00:00:00",
            "name": "Utskottet för det tredje",
            "role": "Ledamot"
        },
        { 
            "start": "2005-01-01T00:00:00",
            "end": "2010-01-01T00:00:00",
            "name": "Utskottet för det andra",
            "role": "Suppleant"
        }
        
    ]
    """

    return json