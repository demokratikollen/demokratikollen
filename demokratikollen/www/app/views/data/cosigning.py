from flask import Blueprint, request, jsonify
from demokratikollen.core.utils.mongodb import MongoDBDatastore

blueprint = Blueprint('data_cosigning', __name__, url_prefix='/data/cosigning')

@blueprint.route('/timeseries.json', methods=['GET'])
def timeseries():
    
    ds = MongoDBDatastore()
    cosigning_data = ds.get_object("party_cosigning_timeseries")
    return jsonify(cosigning_data);
