# -*- coding: utf-8 -*-
from db_structure import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
import utils
import os
import psycopg2 as pg
from progress_bar import InitBar

# Connection to postgres source
source_conn = pg.connect(os.environ['DATABASE_RIKSDAGEN_URL'])

# Connect to SQLAlchemy db and create structure
engine = create_engine(utils.engine_url())
create_db_structure(engine)

session = sessionmaker()
session.configure(bind=engine)
s = session()

parties = [
            "Vänsterpartiet",
            "Socialdemokraterna",
            "Miljöpartiet de gröna",
            "Sverigedemokraterna",
            "Centerpartiet",
            "Folkpartiet liberalerna",
            "Kristdemokraterna",
            "Moderaterna"
        ]

c = source_conn.cursor()
members = {}


# Select all unique combinations of 'organ_kod' and 'uppgift', but exclude 'kam' since these are replacements
# that have names and dates as 'uppgift'
c.execute("SELECT organ_kod,uppgift FROM personuppdrag WHERE organ_kod != 'kam' GROUP BY organ_kod,uppgift")
groups = {}
for abbr,name in c:
    if name in parties:
        g = Party(name=name,abbr=abbr)
        group_or_party = "party"
    else:
        g = Group(name=name,abbr=abbr)
        group_or_party = "group"
    groups[(abbr,name)] = g
    print("Created {} ({}) as a {}.".format(name,abbr,group_or_party))

# Manually add 'Kammaren', and parties not in 'personuppdrag'
groups['-'] = Party(name="Partiobunden",abbr="-")
groups['PP'] = Party(name="Piratpartiet",abbr="PP")
groups['NYD'] = Party(name="Ny demokrati",abbr="NYD")
for g in groups.values():
    s.add(g)

print("Adding members.")
c.execute("SELECT fodd_ar,tilltalsnamn,efternamn,kon,parti,intressent_id FROM person")
for birth_year,first_name,last_name,gender,party_abbr,intressent_id in c:
    if not party_abbr:
        party_abbr = "-"
    try:
        party = s.query(Party).filter(Party.abbr==party_abbr).one()
    except NoResultFound:
        print("No result was found for abbr {}.".format(party_abbr))
        print(party.name)
        raise
    members[intressent_id] = Member(first_name=first_name,last_name=last_name,birth_year=birth_year,gender=gender,party=party)
    s.add(members[intressent_id])
s.commit()

pbar = InitBar(title="Adding votes")
pbar(0)
c.execute("SELECT COUNT(*) FROM votering WHERE avser='sakfrågan'")
num_votes = c.fetchone()[0]
c.execute("SELECT votering_id,intressent_id,beteckning,rm,rost,datum FROM votering WHERE avser='sakfrågan' ORDER BY votering_id")
last_vot_id = None
for i,(votering_id,intressent_id,beteckning,rm,rost,datum) in enumerate(c):
    if last_vot_id!=votering_id:
        date = datum.date()
        poll = Poll(name="{}:{}".format(rm,beteckning),date=date)
        s.add(poll)
        last_vot_id = votering_id
        add_status = 100*i/num_votes
        pbar(add_status)
    if i % 50000 == 0:
        s.commit()
    s.add(Vote(member=members[intressent_id],vote_option=rost,poll=poll))

del pbar

# Add kammaruppdrag
print("Adding chamber appointments.")
c.execute("""SELECT intressent_id,ordningsnummer,"from",tom,status,roll_kod FROM personuppdrag WHERE typ='kammaruppdrag' AND ordningsnummer!=0""")
for intressent_id,ordningsnummer,fr,to,stat,roll in c:
    role = "Ersättare" if "rsättare" in roll else "Riksdagsledamot"
    status = "Ledig" if "Ledig" in stat else "Tjänstgörande"
    s.add(ChamberAppointment(
                member=members[intressent_id],
                chair=ordningsnummer,
                start_date=fr.date(),
                end_date=to.date(),
                status=status,
                role=role))

print("Committing.")
s.commit()
source_conn.close()
