from demokratikollen.core.db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql.expression import literal
from itertools import combinations
from demokratikollen.core.utils import postgres as pg_utils
import datetime as dt
import codecs




def partipiskan():

    engine = create_engine(pg_utils.engine_url())
    session = sessionmaker(bind=engine)
    s = session() 

    parties = s.query(Party).join(Member).join(ChamberAppointment) \
                .filter(ChamberAppointment.start_date > dt.date(2010,10,5)).distinct().all()
    


    for party in parties:
        q = s.query(PartyVote, Poll).join(Poll).join(Party) \
            .filter(Party.id==party.id)\
            .order_by(Poll.date.asc())

        print('{}'.format(party))     

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
                
        print('Piskan viner {}/{}'.format(num_piska,num_polls))
        if len(num_defectors):
            print('Max {}, medel {}'.format(max(num_defectors), sum(num_defectors)/len(num_defectors)))

def main():
    partipiskan()

if __name__ == '__main__':
    main()