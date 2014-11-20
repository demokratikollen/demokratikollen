import os
import datetime
from flask.ext.testing import TestCase
from unittest.mock import MagicMock, Mock, patch

from demokratikollen.www.app import create_app
from demokratikollen.www.app.routes import data


class TestRoutesDataGender(TestCase):
    def create_app(self):
        return create_app(testing=True)

    def setUp(self):
        data.data.gender_json = Mock(return_value=dict(data=[{'test': 1}]))
        data.get_parties = Mock(return_value=['M'])

    def test_gender_json(self):
        response = self.client.get('/data/gender.json')
        self.assert_200(response)

    def test_gender_json_date(self):
        str_date = '2014-01-01'
        #test that it works with a param
        self.client.get('/data/gender.json?date=' + str_date)
        date = datetime.datetime.strptime('2014-01-01', '%Y-%m-%d').date()
        data.data.gender_json.assert_called_with(date=date,party='')

    def test_gender_json_no_date(self):
        self.client.get('/data/gender.json')
        data.data.gender_json.assert_called_with(date=datetime.date.today(),party='')

    def test_gender_json_bad_date(self):
        response = self.client.get('/data/gender.json?date=not_a_date')
        self.assert_400(response)

    def test_gender_json_party(self):
        response = self.client.get('data/gender.json?party=M')

        data.data.gender_json.assert_called_with(date=datetime.date.today(),party='M')

    def test_gender_json_no_party(self):
        response = self.client.get('data/gender.json?party=')

        data.data.gender_json.assert_called_with(date=datetime.date.today(),party='')

    def test_gender_json_bad_party(self):
        response = self.client.get('data/gender.json?party=not-a-pary-abbr')
        self.assert_400(response)

