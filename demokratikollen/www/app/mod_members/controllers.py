# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  json

from sqlalchemy import func,or_,not_,and_
from sqlalchemy.orm import aliased
from datetime import datetime,timedelta
from wtforms import Form, TextField, validators

# Import the database object from the main app module
from demokratikollen.www.app import db, Member, Vote, PolledPoint, ChamberAppointment

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_members = Blueprint('members', __name__, url_prefix='/members')


@mod_members.route('.html')
def members():
    return render_template("/members/members.html")


# Set the route and accepted methods
@mod_members.route('/find', methods=['GET','POST'])
def find():

    form = SearchForm(request.args)
    if not form.terms.data:
        flash({
                "class": "alert-danger",
                "title": "Ingen indata:",
                "text": "Du angav inget att söka på."
            })
        return redirect('/members.html')

    s_words = [w.lower() for w in form.terms.data.split()]

    q = db.session.query(Member)

    for w in s_words:
        q = q.filter(or_(
                    func.lower(Member.first_name).like('%{}%'.format(w)),
                    func.lower(Member.last_name).like('%{}%'.format(w))))

    members = q.all()
    if len(members) == 0:
        flash({
                "class": "alert-warning",
                "text": "Din sökning matchade inga ledamöter."
            })
        return redirect('/members.html')
    else:
        return render_template("/members/members.html",form=form,members=members)

# Set the route and accepted methods
@mod_members.route('/<int:member_id>.html')
def member(member_id):
    m = db.session.query(Member).filter_by(id=member_id).first()

    return render_template("/members/member.html",member=m)

@mod_members.route('/ajax/<int:member_id>.html')
def member_ajax(member_id):
    m = db.session.query(Member).filter_by(id=member_id).one()
    return render_template("/members/member_ajax.html",member=m)

# Helper to construct typeahead responses
def typeahead_response(members):
    output = {"d": [{
                        "full_name": "{} {}".format(m.first_name,m.last_name),
                        "party": m.party.abbr,
                        "id": m.id
                    } for m in members]}
    return json.jsonify(output)


@mod_members.route('/typeahead/current.json')
def th_current():
    now = datetime.utcnow()
    members = db.session.query(Member).join(ChamberAppointment) \
                    .filter(ChamberAppointment.end_date > now,
                            ChamberAppointment.start_date < now,
                            ChamberAppointment.status != "Ledig")
    return typeahead_response(members)

# Set the route and accepted methods
@mod_members.route('/typeahead/query.json',methods=['GET'])
def th_query():
    s_words = [w.lower() for w in request.args['q'].split()]
    db_q = db.session.query(Member)

    now = datetime.utcnow()
    db_q = db_q.join(ChamberAppointment) \
                    .filter(not_(and_(ChamberAppointment.end_date > now,
                            ChamberAppointment.start_date < now,
                            ChamberAppointment.status != "Ledig")))
    for w in s_words:
        db_q = db_q.filter(or_(
                    func.lower(Member.first_name).like('%{}%'.format(w)),
                    func.lower(Member.last_name).like('%{}%'.format(w))))

    print(db_q)
    return typeahead_response(db_q.all())


@mod_members.route('/<int:member_id>/absence.json', methods=['GET'])
def get_member(member_id):
    """Return a JSON response with total and absent votes monthly for member"""
    y = func.date_part('year',PolledPoint.date).label('y')
    m = func.date_part('month',PolledPoint.date).label('m')

    q = db.session.query(Vote.vote_option,func.count(Vote.id),y,m) \
                            .join(PolledPoint).filter(Vote.member_id==member_id) \
                            .group_by(Vote.vote_option,'y','m') \
                            .order_by('y','m')

    def month_iter(start,end):
        cur_y,cur_m = start
        y2,m2 = end
        while not (cur_y >= y2 and cur_m >= m2):
            yield cur_y,cur_m
            cur_m += 1
            if cur_m > 12:
                cur_y += 1
                cur_m = 1
        yield cur_y, cur_m

    tot = {}
    absent = {}

    for vo,num,y,m in q:
        if not (y,m) in tot:
            tot[(y,m)] = num
        else:
            tot[(y,m)] += num
        if vo == 'Frånvarande':
            absent[(y,m)] = num


    nvd3_data={
        "d": [
            {
                "key": "Frånvarande",
                "values": []
            },
            {
                "key": "Totalt",
                "values": []
            }
        ]
    }

    results = q.all()
    if len(results)==0:
        return json.jsonify(nvd3_data)
    start = results[0][2:]
    end = results[-1][2:]

    for y,m in month_iter(start,end):
        absence = 0 if not (y,m) in absent else absent[(y,m)]
        total = 0 if not (y,m) in tot else tot[(y,m)]

        nvd3_data["d"][0]["values"] \
            .append({
                "x": datetime(year=int(y),month=int(m),day=1).timestamp(),
                "y": absence})
        nvd3_data["d"][1]["values"] \
            .append({
                "x": datetime(year=int(y),month=int(m),day=1).timestamp(),
                "y": total})

    return json.jsonify(nvd3_data)


