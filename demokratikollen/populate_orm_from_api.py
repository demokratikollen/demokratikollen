# -*- coding: utf-8 -*-
import urllib.request as request
import json
from datetime import datetime as dt
from demokratikollen.core.db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from demokratikollen.core.utils import postgres as pg_utils
import logging
import pdb


# Configure logging
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('[%(levelname)8s] %(message)s'))
root_logger.addHandler(ch)

logger = logging.getLogger(__name__)

# Connect to SQLAlchemy db and create structure
engine = create_engine(pg_utils.engine_url())
create_db_structure(engine, do_not_confirm=True)

session = sessionmaker()
session.configure(bind=engine)
s = session()

# Manually specify parties for simplicity
party_names_abbrs = [
            ("V","Vänsterpartiet"),
            ("S","Socialdemokraterna"),
            ("MP","Miljöpartiet de gröna"),
            ("SD","Sverigedemokraterna"),
            ("C","Centerpartiet"),
            ("FP","Folkpartiet liberalerna"),
            ("KD","Kristdemokraterna"),
            ("M","Moderaterna"),
            ("NYD","Ny demokrati"),
            ("PP","Piratpartiet"),
            ("-","Partiobunden")
        ]

logger.info("Adding parties.")
parties = {abbr: Party(name=name,abbr=abbr) for abbr,name in party_names_abbrs}
group_objs = {}
for g in parties.values():
    group_objs[(g.abbr,g.name)] = g
    s.add(g)

# TODO: Use full member list
# members_url = 'http://data.riksdagen.se/personlista/?rdlstatus=samtliga&utformat=json'

# NB: Only current members.
members_url = 'http://data.riksdagen.se/personlista/?utformat=json'

logger.info("Retrieving member data.")
logger.debug("Reading from {}".format(members_url))
with request.urlopen(members_url) as response:
    data = json.loads(response.read().decode('utf-8-sig'))
    members = data["personlista"]["person"]

member_objs = {}
logger.info("Adding members.")
for member in members:
    logger.debug("Adding {}, (iid: {}).".format(member["sorteringsnamn"],member["intressent_id"]))
    intressent_id = member["intressent_id"]

    try:
        party = parties[member["parti"].upper()]
    except KeyError:
        party = parties["-"]

    member_objs[intressent_id] = Member(intressent_id=intressent_id,
                                        first_name=member["tilltalsnamn"],last_name=member["efternamn"],
                                        birth_year=member["fodd_ar"],gender=member["kon"],party=party,
                                        image_url_md=member["bild_url_192"],
                                        image_url_lg=member["bild_url_max"],
                                        image_url_sm=member["bild_url_80"],
                                        url_name='')
    s.add(member_objs[intressent_id])

def create_chamber_appointment(app):
    role = "Ersättare" if "rsättare" in app["roll_kod"] else "Riksdagsledamot"
    status = "Ledig" if "Ledig" in app["status"] else "Tjänstgörande"
    start_date = dt.strptime(app["from"], "%Y-%m-%d").date()
    end_date = dt.strptime(app["tom"], "%Y-%m-%d").date()
    logger.debug("Creating a chamber appointment from {} to {} as {} {}.".format(start_date,end_date,
                                                                                    status,role))
    return ChamberAppointment(
                member=member_objs[app["intressent_id"]],
                chair=app["ordningsnummer"],
                start_date=start_date,
                end_date=end_date,
                status=status,
                role=role)

def get_or_create_group(abbr,name,cls):
    try:
        return group_objs[(abbr,name)]
    except KeyError:
        logger.debug("Creating {} ({}) as a {}.".format(name,abbr,cls.__name__))
        group_objs[(abbr,name)] = cls(abbr=abbr,name=name)
        return group_objs[(abbr,name)]

def create_group_appointment(app):
    # Ministries
    if "epartement" in app["uppgift"]:
        group_cls = Ministry
        app_cls = MinistryAppointment
    # Committees
    elif "utskott" in app["uppgift"]:
        group_cls = Committee
        app_cls = CommitteeAppointment
    else:
        group_cls = Group
        app_cls = GroupAppointment

    g = get_or_create_group(abbr=app["organ_kod"],name=app["uppgift"],cls=group_cls)
    start_date = dt.strptime(app["from"], "%Y-%m-%d").date()
    end_date = dt.strptime(app["tom"], "%Y-%m-%d").date()

    logger.debug("Creating a {} in {} ({}) from {} to {} as {}.".format(app_cls.__name__,
                                                                        app["uppgift"],
                                                                        app["organ_kod"],
                                                                        start_date,end_date,
                                                                        app["roll_kod"]))
    return app_cls(member=member_objs[app["intressent_id"]],
                start_date=start_date,
                end_date=end_date,
                role=app["roll_kod"],
                group=g)
    

logger.info("Adding appointments.")
for member in members:
    logger.debug("Appointments for {}.".format(member["sorteringsnamn"]))
    for appointment in member["personuppdrag"]["uppdrag"]:
        if appointment["organ_kod"]=="kam":
            if appointment["typ"]=="kammaruppdrag":
                s.add(create_chamber_appointment(appointment))
            else:
                # TODO: Add other chamber appointments.
                # Can be "typ": "talmansuppdrag". Other possibilities?
                pass
        else:
            s.add(create_group_appointment(appointment))


logger.info("Committing.")
s.commit()
