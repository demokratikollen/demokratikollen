# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  json

from sqlalchemy import func
from sqlalchemy.orm import aliased
from datetime import datetime,timedelta

# Import the database object from the main app module
from demokratikollen.www.app import db, Member, Vote, Poll

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_members = Blueprint('members', __name__, url_prefix='/members')

# Set the route and accepted methods
@mod_members.route('/find', methods=['GET'])
def find_member():
    fn = None if not 'fn' in request.args else request.args['fn']
    ln = None if not 'ln' in request.args else request.args['ln']

    q = db.session.query(Member)

    if fn:
        q = q.filter(func.lower(Member.first_name).like('%{}%'.format(fn)))
    if ln:
        q = q.filter(func.lower(Member.last_name).like('%{}%'.format(ln)))

    return render_template("/members/members.html",members=q.all())

# Set the route and accepted methods
@mod_members.route('/<int:member_id>', methods=['GET'])
def member(member_id):
    try:
        format = request.args['format']
    except KeyError:
        format = None
    m = db.session.query(Member).filter_by(id=member_id).first()

    if format=='json':
        member = {
            "first_name": m.first_name,
            "last_name": m.last_name
        }
        return json.jsonify(member)
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

    # Sort result into output format
    res_dict = {}
    for vo,num,y,m in q:
        if not y in res_dict:
            res_dict[y] = {}
        if not m in res_dict[y]:
            res_dict[y][m] = {}
        if not 'Totalt' in res_dict[y][m]:
            res_dict[y][m]['Totalt'] = num
        else:
            res_dict[y][m]['Totalt'] += num
        if vo == 'Frånvarande':
            res_dict[y][m][vo] = num

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

    for y,rd_y in res_dict.items():
        for m,rd_ym in rd_y.items():
            try:
                nvd3_data["d"][0]["values"] \
                    .append({
                        "x": datetime(year=int(y),month=int(m),day=1).timestamp(),
                        "y": rd_ym['Frånvarande']})
            except KeyError:
                pass
            try:
                nvd3_data["d"][1]["values"] \
                    .append({
                        "x": datetime(year=int(y),month=int(m),day=1).timestamp(),
                        "y": rd_ym['Totalt']})
            except KeyError:
                pass

    return json.jsonify(nvd3_data)

