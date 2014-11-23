import os
from subprocess import call
from datetime import date
from flask.ext.testing import TestCase
from unittest.mock import MagicMock

from demokratikollen.www.app.helpers.db import db
from demokratikollen.www.app import create_app
from demokratikollen.www.app.models import data
from demokratikollen.core.db_structure import Member, ChamberAppointment, Base, Party

d = date(2014,1,1)

def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

class TestGenderJson(TestCase):

    def create_app(self):
        return create_app(testing=True)

    def setUp(self):
        Base.metadata.create_all(db.engine)

        members = []

        #Add the standard members.
        member_elected_female = Member(gender='kvinna')
        member_elected_female.party = Party(abbr='S')
        member_elected_female.appointments = [ChamberAppointment(role='Riksdagsledamot',start_date=add_years(d,-1),end_date=add_years(d,1))]
        members.append(member_elected_female)

        member_elected_male = Member(gender='man')
        member_elected_male.party = Party(abbr='S')
        member_elected_male.appointments = [ChamberAppointment(role='Riksdagsledamot',start_date=add_years(d,-1),end_date=add_years(d,1))]
        members.append(member_elected_male)

        member_not_elected = Member()
        member_not_elected.party = Party(abbr='S')
        member_not_elected.appointments= [ChamberAppointment(role='Ersättare',start_date=add_years(d,-1),end_date=add_years(d,1))]
        members.append(member_not_elected)

        member_outside = Member()
        member_outside.party = Party(abbr='S')
        member_outside.appointments = [ChamberAppointment(role='Riksdagsledamot',start_date=add_years(d,-2),end_date=add_years(d,-1))]
        members.append(member_outside)


        for member in members:
            db.session.add(member)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        Base.metadata.drop_all(db.engine)

    def test_only_elected_members_should_be_returned(self):
        response = data.gender_json(date=d)

        member_not_elected = Member()
        member_not_elected.party = Party(abbr='S')
        member_not_elected.appointments= [ChamberAppointment(role='Ersättare',start_date=add_years(d,-1),end_date=add_years(d,1))]
        db.session.add(member_not_elected)

        self.assertEqual(len(response['data']), 2 )

    def test_appointments_inside_date_are_returned(self):
        response = data.gender_json(date=d)

        member_outside = Member()
        member_outside.party = Party(abbr='S')
        member_outside.appointments = [ChamberAppointment(role='Riksdagsledamot',start_date=add_years(d,-2),end_date=add_years(d,-1))]
        db.session.add(member_outside)

        self.assertEqual(len(response['data']), 2 )

    def test_sets_correct_stats(self):
        response = data.gender_json(date=d)

        self.assertEqual(len(response['data']), 2 )
        self.assertEqual(response['statistics']['n_males'], 1)
        self.assertEqual(response['statistics']['n_females'], 1)
        self.assertEqual(response['statistics']['total'], 2)

    def test_sets_corrcet_party(self):
        response = data.gender_json(date=d)

        self.assertEqual(len(response['data']), 2 )
        self.assertEqual(response['data'][0]['party'], 'S')

    def test_only_returns_correct_party(self):
        member_elected_male_M = Member(gender='man')
        member_elected_male_M.party = Party(abbr='M')
        member_elected_male_M.appointments = [ChamberAppointment(role='Riksdagsledamot',start_date=add_years(d,-1),end_date=add_years(d,1))]

        db.session.add(member_elected_male_M)

        response = data.gender_json(date=d, party='M')

        self.assertEqual(len(response['data']), 1)
        self.assertEqual(response['data'][0]['party'], 'M')

