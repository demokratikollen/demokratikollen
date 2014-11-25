# Import the database object from the main app module
from demokratikollen.www.app.helpers.db import db
from demokratikollen.www.app.helpers.cache import cache
from demokratikollen.core.db_structure import Member, ChamberAppointment, Party

def gender_json(date,party=''):

    members = get_gender_db_statement(date,party);    
    print(members.all())

    response = {'statistics': {'n_males': 0, 'n_females': 0, 'total': 0}, 'data': [], }
    for member in members.all():
        response['data'].append(dict(member_id=member[0],gender=member[1],party=member[2]))
        if member[1] == 'kvinna':
            response['statistics']['n_females'] += 1
        else:
            response['statistics']['n_males'] += 1
        response['statistics']['total'] += 1

    # sort the data on party. 
    response['data'] = sorted(response['data'], key=lambda k: k['party'])

    return response

def get_gender_db_statement(date, party=''):
    members = db.session.query(Member.id, Member.gender, Party.abbr). \
                join(ChamberAppointment). \
                join(Party). \
                filter(ChamberAppointment.role=='Riksdagsledamot'). \
                filter(ChamberAppointment.start_date <= date). \
                filter(ChamberAppointment.end_date >= date) .\
                distinct(Member.id)
    if party:
        members = members.filter(Party.abbr==party)

    return members

def parliament_json(date):

    members = get_parliament_db_statement(date)
   
    response = {'statistics': {'n_members': 0}, 'data': [], }
    for member in members.all():
        response['data'].append(dict(member_id=member[0],party=member[1]))
        response['statistics']['n_members'] += 1

    # sort the data on party. 
    response['data'] = sorted(response['data'], key=lambda k: k['party'])

    return response

def get_parliament_db_statement(date):
    members = db.session.query(Member.id, Party.abbr). \
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

