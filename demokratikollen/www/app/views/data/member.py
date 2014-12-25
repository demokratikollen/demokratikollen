import datetime
import json

from flask import Blueprint, request, jsonify

from demokratikollen.www.app.helpers.db import db
from demokratikollen.www.app.helpers.cache import cache
from demokratikollen.core.db_structure import Member, Appointment, \
        CommitteeAppointment, ChamberAppointment, GroupAppointment, Group, Party
from sqlalchemy import and_, desc
from sqlalchemy.orm import joinedload, with_polymorphic
import datetime

from flask.ext.jsontools import jsonapi

blueprint = Blueprint('data_member', __name__, url_prefix='/data/member')

@blueprint.route('/<int:member_id>/appointments.json', methods=['GET'])
@jsonapi
def appointments_json(member_id):
    appointments = db.session.query(with_polymorphic(Appointment, '*'), Group) \
        .filter(Appointment.member_id == member_id) \
        .outerjoin(Group) \
        .all()

    return appointments
