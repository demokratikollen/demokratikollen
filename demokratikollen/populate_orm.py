# -*- coding: utf-8 -*-
from demokratikollen.core.db_structure import *
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from demokratikollen.core.utils import postgres as pg_utils
import os
import psycopg2 as pg
from progress_bar import InitBar

# Connection to postgres source
source_conn = pg.connect(os.environ['DATABASE_RIKSDAGEN_URL'])

# Connect to SQLAlchemy db and create structure
engine = create_engine(pg_utils.engine_url())
create_db_structure(engine, do_not_confirm=True)

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
print("Adding groups, committees, and parties.")
for abbr,name in c:
    if name in parties:
        g = Party(name=name,abbr=abbr)
    elif 'tskott' in name:
        g = Committee(name=name,abbr=abbr)
    elif 'epartement' in name:
        g = Ministry(name=name,abbr=abbr)
    else:
        g = Group(name=name,abbr=abbr)
    groups[(abbr,name)] = g

# Manually add 'Kammaren', and parties not in 'personuppdrag'
groups['-'] = Party(name="Partiobunden",abbr="-")
groups['PP'] = Party(name="Piratpartiet",abbr="PP")
groups['NYD'] = Party(name="Ny demokrati",abbr="NYD")
for g in groups.values():
    s.add(g)
# s.commit()

print("Adding members.")
c.execute("SELECT fodd_ar,tilltalsnamn,efternamn,kon,parti,intressent_id FROM person")
for birth_year,first_name,last_name,gender,party_abbr,intressent_id in c:
    if not party_abbr:
        party_abbr = "-"
    try:
        party = s.query(Party).filter(Party.abbr==party_abbr).one()
    except NoResultFound:
        print("No result was found for abbr {}.".format(party_abbr))
        raise
    members[intressent_id] = Member(first_name=first_name,last_name=last_name,
                                    birth_year=birth_year,gender=gender,party=party,
                                    image_url="http://data.riksdagen.se/filarkiv/bilder/ledamot/{}_192.jpg".format(intressent_id))
    s.add(members[intressent_id])
# s.commit()

# Select only betänkanden from dokument
print("Adding committee reports.")
c.execute("""SELECT dok_id,rm,beteckning,organ,publicerad,titel,dokument_url_text,hangar_id FROM dokument WHERE doktyp='bet' AND relaterat_id=''""")
reports = {}
for dok_id,rm,bet,organ,publ,titel,dok_url,hangar_id in c:
    committee = s.query(Committee).filter_by(abbr=organ).one()
    s.add(CommitteeReport(
            dok_id=dok_id,
            published=publ,
            session=rm,
            code=bet,
            title=titel,
            text_url=dok_url,
            committee=committee))
# s.commit()

pbar = InitBar(title="Adding votes")
pbar(0)
polls = {}
c.execute("SELECT COUNT(*) FROM votering WHERE avser='sakfrågan'")
num_votes = c.fetchone()[0]
c_named = source_conn.cursor("named")
c_named.itersize = 50000
c_named.execute("SELECT votering_id,intressent_id,beteckning,rm,punkt,rost,datum FROM votering WHERE avser='sakfrågan' ORDER BY votering_id")
for i,(votering_id,intressent_id,beteckning,rm,punkt,rost,datum) in enumerate(c_named):
    if votering_id not in polls:
        date = datum.date()
        polls[votering_id] = PolledPoint(poll_date=date,r_votering_id=votering_id,number=punkt)
        s.add(polls[votering_id])
    if i % 1000 == 0:
        add_status = 100*i/num_votes
        pbar(add_status)
    if i % 50000 == 0:
        s.commit()
    s.add(Vote(member=members[intressent_id],
                vote_option=rost,polled_point=polls[votering_id]))

del pbar
# s.commit()

# Add kammaruppdrag
print("Adding chamber appointments.")
c.execute("""SELECT intressent_id,ordningsnummer,"from",tom,status,roll_kod FROM personuppdrag WHERE typ='kammaruppdrag'""")
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
# s.commit()

# Add ministry (departement) appointments
print("Adding ministry appointments.")
c.execute("""SELECT intressent_id,"from",tom,roll_kod,organ_kod,uppgift FROM personuppdrag WHERE uppgift LIKE '%epartement%'""")
for intressent_id,fr,to,roll,abbr,g_name in c:
    s.add(MinistryAppointment(
                member=members[intressent_id],
                start_date=fr.date(),
                end_date=to.date(),
                role=roll,
                group=groups[(abbr,g_name)]))

# Add committee (utskott) appointments
print("Adding committee appointments.")
c.execute("""SELECT intressent_id,"from",tom,roll_kod,organ_kod,uppgift FROM personuppdrag WHERE uppgift LIKE '%utskott%'""")
for intressent_id,fr,to,roll,abbr,g_name in c:
    s.add(CommitteeAppointment(
                member=members[intressent_id],
                start_date=fr.date(),
                end_date=to.date(),
                role=roll,
                group=groups[(abbr,g_name)]))

# Add other group appointments
print("Adding other group appointments.")
c.execute("""SELECT intressent_id,"from",tom,roll_kod,organ_kod,uppgift FROM personuppdrag
                WHERE NOT uppgift  LIKE '%utskott%' AND NOT uppgift LIKE '%utskott%' AND organ_kod != 'kam'""")
for intressent_id,fr,to,roll,abbr,g_name in c:
    s.add(GroupAppointment(
                member=members[intressent_id],
                start_date=fr.date(),
                end_date=to.date(),
                role=roll,
                group=groups[(abbr,g_name)]))

# s.commit()

print("Adding member proposals.")
c.execute("""SELECT hangar_id,dok_id,rm,beteckning,publicerad,titel,
                            dokument_url_text,subtyp
                    FROM dokument WHERE doktyp='mot' AND relaterat_id='' ORDER BY hangar_id""")
m_props = {}
for hangar_id,dok_id,rm,beteckning,publicerad,titel,dokument_url_text,subtyp in c:
    if subtyp in ['Enskild motion','Kommittémotion','Följdmotion','Partimotion','Flerpartimotion','Fristående motion']:
        subtype = subtyp
    else:
        subtype = '-'
    if hangar_id in m_props:
        raise Exception('Member proposal with hangar_id {} already exists.'.format(hangar_id))
    m_props[hangar_id] = MemberProposal(
                            dok_id=dok_id,
                            published=publicerad,
                            session=rm,
                            code=beteckning,
                            title=titel,
                            text_url=dokument_url_text,
                            subtype=subtype)
    s.add(m_props[hangar_id])

print("Adding signatories of member proposals.")
c.execute("""SELECT d.hangar_id,i.intressent_id FROM dokument AS d
                JOIN dokintressent AS i ON i.hangar_id=d.hangar_id
                WHERE d.doktyp='mot' ORDER BY d.hangar_id""")
for hangar_id,intressent_id in c:
    m_props[hangar_id].signatories.append(members[intressent_id])


print("Adding points of member proposals.")
c.execute("""SELECT d.hangar_id,f.utskottet,f.nummer,f.kammaren,f.behandlas_i
                FROM dokument AS d
                JOIN dokforslag AS f ON f.hangar_id=d.hangar_id
                WHERE d.doktyp='mot' ORDER BY d.hangar_id""")
m_missing_crs = 0
m_props_tot = 0
for hangar_id,utskottet,nummer,kammaren,behandlas_i in c:
    decision_options = ['Avslag','Bifall','Delvis bifall']
    utskottet = utskottet.strip()
    kammaren = kammaren.strip()

    if kammaren in decision_options:
        ch_decision = kammaren
    else:
        ch_decision = '-'

    if utskottet in decision_options:
        com_recommendation = utskottet
    else:
        com_recommendation = '-'

    try:
        m_props_tot += 1
        rm,bet = behandlas_i.split(':')
        cr = s.query(CommitteeReport).filter(CommitteeReport.session==rm,
                func.lower(CommitteeReport.code)==bet.lower()).one()
        p = ProposalPoint(
                proposal=m_props[hangar_id],
                number=nummer,
                committee_recommendation=com_recommendation,
                decision=ch_decision,
                committee_report=cr)
    except (ValueError,NoResultFound) as e:
        m_missing_crs += 1
        p = ProposalPoint(
                proposal=m_props[hangar_id],
                number=nummer,
                committee_recommendation=com_recommendation,
                decision=ch_decision)

    s.add(p)
print("{} of {} member proposal points missing committee report.".format(m_missing_crs,m_props_tot))

print("Adding government proposals.")
c.execute("""SELECT hangar_id,dok_id,rm,beteckning,publicerad,titel,
                            dokument_url_text,organ
                    FROM dokument WHERE doktyp='prop' AND relaterat_id='' AND subtyp='prop'
                    ORDER BY hangar_id""")
g_props = {}
g_missing_ministry = 0
g_tot = 0
for hangar_id,dok_id,rm,beteckning,publicerad,titel,dokument_url_text,organ in c:
    if hangar_id in g_props:
        raise Exception('Government proposal with hangar_id {} already exists.'.format(hangar_id))
    try:
        g_tot += 1
        m = s.query(Ministry).filter(func.lower(Ministry.abbr)==organ.lower()).one()
    except NoResultFound as e:
        try:
            m = s.query(Ministry).filter(func.lower(Ministry.name)==organ.lower()).one()
        except NoResultFound as e:
            g_missing_ministry += 1
            m = None

    if not m:
        g_props[hangar_id] = GovernmentProposal(
                                    dok_id=dok_id,
                                    published=publicerad,
                                    session=rm,
                                    code=beteckning,
                                    title=titel,
                                    text_url=dokument_url_text)
    else:
        g_props[hangar_id] = GovernmentProposal(
                                    dok_id=dok_id,
                                    published=publicerad,
                                    session=rm,
                                    code=beteckning,
                                    title=titel,
                                    text_url=dokument_url_text,
                                    ministry=m)
    s.add(g_props[hangar_id])
print("{} of {} government proposals missing ministry.".format(g_missing_ministry,g_tot))


print("Adding points of government proposals.")
c.execute("""SELECT d.hangar_id,f.utskottet,f.nummer,f.kammaren,f.behandlas_i
                FROM dokument AS d
                JOIN dokforslag AS f ON f.hangar_id=d.hangar_id
                WHERE d.doktyp='prop' AND d.subtyp='prop' ORDER BY d.hangar_id""")
g_props_tot = 0
g_prop_missing = 0
g_missing_crs = 0
# g_missing_crs_list = []
for hangar_id,utskottet,nummer,kammaren,behandlas_i in c:
    decision_options = ['Avslag','Bifall','Delvis bifall']
    utskottet = utskottet.strip()
    kammaren = kammaren.strip()

    if kammaren in decision_options:
        ch_decision = kammaren
    else:
        ch_decision = '-'

    if utskottet in decision_options:
        com_recommendation = utskottet
    else:
        com_recommendation = '-'

    if hangar_id not in g_props:
        g_prop_missing += 1
        continue

    try:
        g_props_tot += 1
        rm,bet = behandlas_i.split(':')
        cr = s.query(CommitteeReport).filter(CommitteeReport.session==rm,
                func.lower(CommitteeReport.code)==bet.lower()).one()
        p = ProposalPoint(
                proposal=g_props[hangar_id],
                number=nummer,
                committee_recommendation=com_recommendation,
                decision=ch_decision,
                committee_report=cr)
    except (ValueError,NoResultFound) as e:
        g_missing_crs += 1
        # g_missing_crs_list.append((hangar_id,nummer,behandlas_i))
        # if g_missing_crs >= 10:
        #     for missing_cr in g_missing_crs_list:
        #         print("{}, punkt {}: {} saknas.".format(missing_cr[0],missing_cr[1],missing_cr[2]))
        #     exit()
        p = ProposalPoint(
                proposal=g_props[hangar_id],
                number=nummer,
                committee_recommendation=com_recommendation,
                decision=ch_decision)

    s.add(p)
print("{} government proposal points missing proposal document.".format(g_prop_missing))
print("{} of {} government proposal points missing committee report.".format(g_missing_crs,g_props_tot))

print("Adding committee report points")
c.execute("""SELECT rm,bet,punkt,rubrik,beslutstyp,votering_id FROM dokutskottsforslag""")
for rm,bet,punkt,rubrik,beslutstyp,votering_id in c:
    try:
        if not votering_id:
            rep = s.query(CommitteeReport).filter(CommitteeReport.session==rm,
                            func.lower(CommitteeReport.code)==bet.lower()).one()
            s.add(AcclaimedPoint(
                    number=punkt,
                    title=rubrik,
                    report=rep))
        else:
            point = s.query(PolledPoint).filter_by(r_votering_id=votering_id).one()
            point.title = rubrik
    except NoResultFound:
        pass

print("Committing.")
s.commit()
source_conn.close()
