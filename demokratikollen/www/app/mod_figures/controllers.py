# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  json

from demokratikollen.www.app import db, PartyVote, Poll, Party, Member, ChamberAppointment
from sqlalchemy import func

import datetime as dt
import calendar

mod_figures = Blueprint('figures', __name__, url_prefix='/figures')

########
# Routes

@mod_figures.route('/voteringsfrekvens.<string:format>')
def voteringsfrekvens(format):
    if format == 'html':
        return render_template('/figures/voteringsfrekvens.html')
    if format == 'json':
        poll_agg = db.session.query(func.date_trunc('week', Poll.date), func.count(Poll.id)) \
                    .group_by(func.date_trunc('week', Poll.date))  \
                    .order_by(func.date_trunc('week', Poll.date))

        data = []
        for poll in poll_agg:
            data.append(dict(label=poll[0].strftime('%m-%d'), value=poll[1]))

        return json.jsonify(key='voteringsfrekvens', values=data)
    else:
        return render_template('404.html'), 404

@mod_figures.route('/partipiskan', methods=['GET'])
def partipiskan():

    s = db.session

    parties = s.query(Party).join(Member).join(ChamberAppointment) \
                .filter(ChamberAppointment.start_date > dt.date(2010,10,5)).distinct().all()

    data = dict(key="% Polls with party split", values=list())

    for party in parties:
        q = s.query(PartyVote, Poll).join(Poll).join(Party) \
            .filter(Party.id==party.id)\
            .order_by(Poll.date.asc())

        num_polls = 0
        num_piska = 0
        num_defectors = list()
        for (pv, poll) in q:
            counts = [pv.num_yes, pv.num_no, pv.num_abstain]
            winner = max(counts)
            total = sum(counts)
            grand_total = total + pv.num_absent
            num_polls += 1
            if winner != total: 
                num_piska += 1
                num_defectors.append(total-winner)
                
        
        data['values'].append( dict(label=party.abbr, value=num_piska/num_polls) )




    return render_template("/figures/partipiskan.html",
                            header_figures_class='active',
                            header_partipiskan_class='active',
                            data = data)

