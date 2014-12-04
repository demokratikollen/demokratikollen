from flask import Blueprint, request, jsonify
# from demokratikollen.www.app.models import parties

import datetime

blueprint = Blueprint('parties', __name__, url_prefix='/parties')
