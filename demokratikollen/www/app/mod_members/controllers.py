# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  json

from sqlalchemy import func
from sqlalchemy.orm import aliased
from datetime import datetime,timedelta
from wtforms import Form, TextField, validators

# Import the database object from the main app module
from demokratikollen.www.app import db, Member, Vote, Poll

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_members = Blueprint('members', __name__, url_prefix='/members')

class SearchForm(Form):
    first_name = TextField('Förnamn')
    last_name = TextField('Efternamn')

@mod_members.route('/')
def members():
    form = SearchForm()
    return render_template("/members/members.html",form=form)


# Set the route and accepted methods
@mod_members.route('/find', methods=['GET','POST'])
def find_member():
    form = SearchForm(request.form)
    fn = form.first_name.data
    ln = form.last_name.data

    if not fn and not ln:
        flash({
                "class": "alert-danger",
                "title": "Ingen indata:",
                "text": "Du angav inget att söka på."
            })
        return redirect('/members')

    q = db.session.query(Member)

    if fn:
        q = q.filter(func.lower(Member.first_name).like('%{}%'.format(fn.lower())))
    if ln:
        q = q.filter(func.lower(Member.last_name).like('%{}%'.format(ln.lower())))

    members = q.all()
    if len(members) == 0:
        flash({
                "class": "alert-warning",
                "text": "Din sökning matchade inga ledamöter."
            })
        return redirect('/members')
    else:
        return render_template("/members/members.html",form=form,members=members)

# Set the route and accepted methods
@mod_members.route('/<int:member_id>', methods=['GET'])
def member(member_id):
    try:
        format = request.args['format']
    except KeyError:
        format = None
    m = db.session.query(Member).filter_by(id=member_id).first()

    return render_template("/members/member.html",member=m)



@mod_members.route('/<int:member_id>/absence', methods=['GET'])
def get_member(member_id):
    """Return a JSON response with total and absent votes monthly for member"""

    y = func.date_part('year',Poll.date).label('y')
    m = func.date_part('month',Poll.date).label('m')

    q = db.session.query(Vote.vote_option,func.count(Vote.id),y,m) \
                            .join(Poll).filter(Vote.member_id==member_id) \
                            .group_by(Vote.vote_option,'y','m') \
                            .order_by('y','m')

    def month_iter(start,end):
        cur_y,cur_m = start
        y2,m2 = end
        while not (cur_y >= y2 and cur_m > m2):
            yield cur_y,cur_m
            cur_m += 1
            if cur_m > 12:
                cur_y += 1
                cur_m = 1

    results = q.all()
    start = results[0][2:]
    end = results[-1][2:]

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

