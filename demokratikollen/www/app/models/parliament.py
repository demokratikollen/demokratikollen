# Import the database object from the main app module
from demokratikollen.www.app.helpers.db import db
from demokratikollen.www.app.helpers.cache import cache
from demokratikollen.core.db_structure import Member, Appointment, \
        CommitteeAppointment, ChamberAppointment, GroupAppointment, Group, Party
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from datetime import datetime
from demokratikollen.www.app.models.parties import party_comparator

@cache.memoize(3600*24)
def parliament(date):

    members = get_parliament_db_statement(date)

    response = {'statistics': {'n_members': 0}, 'data': [], }
    for member in members.all():
        response['data'].append(dict(member_id=member[0],party=member[1], url_name=member[2], image_url=member[3], name=(member[4] + " " + member[5])))
        response['statistics']['n_members'] += 1

    # sort the data on party.
    response['data'] = sorted(response['data'], key=lambda member: party_comparator(member['party']))

    return response

def get_parliament_db_statement(date):
    members = db.session.query(Member.id, Party.abbr, Member.url_name, Member.image_url_md, Member.first_name, Member.last_name). \
                join(ChamberAppointment). \
                join(Party). \
                filter(ChamberAppointment.role=='Riksdagsledamot'). \
                filter(ChamberAppointment.start_date <= date). \
                filter(ChamberAppointment.end_date >= date) .\
                distinct(Member.id)
    return members

@cache.cached(3600*24)
def get_parties():
    return [r[0] for r in db.session.query(Party.abbr).all()]


@cache.cached(3600*24)
def get_members_typeahead():
    members = db.session.query(Member).options(joinedload(Member.party),joinedload(Member.current_group_appointments).joinedload(GroupAppointment.group)).all()

    output = {"d": [{
                        "fullName": "{} {}".format(m.first_name,m.last_name),
                        "party": m.party.name.split()[0],
                        "id": m.id,
                        "groups": ' '.join([a.group.name for a in m.current_group_appointments])
                    } for m in members]}
    return output

