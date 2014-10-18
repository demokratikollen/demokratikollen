# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  json

from app import db, PartyVote, Poll, Party, Member, ChamberAppointment

import datetime as dt

mod_figures = Blueprint('figures', __name__, url_prefix='/figures')

########
# Routes

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

