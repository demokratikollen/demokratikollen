import os
import datetime
from flask.ext.testing import TestCase
from unittest.mock import MagicMock, Mock, patch

from demokratikollen.www.app import create_app
from demokratikollen.www.app.views import data


class TestRoutesDataGenderJson(TestCase):
    def create_app(self):
        return create_app(testing=True)

    @classmethod
    def setUpClass(cls):
        cls.uri = '/data/gender.json'
        data.data.gender_json = Mock(return_value=dict(data=[{'test': 1}]))
        data.data.get_parties = Mock(return_value=['M'])

    def test_basic_route(self):
        response = self.client.get(self.uri)
        self.assert_200(response)

    def test_date_param(self):
        str_date = '2014-01-01'
        #test that it works with a param
        self.client.get(self.uri + '?date=' + str_date)
        date = datetime.datetime.strptime('2014-01-01', '%Y-%m-%d').date()
        data.data.gender_json.assert_called_with(date=date,party='')

    def test_no_date(self):
        self.client.get(self.uri)
        data.data.gender_json.assert_called_with(date=datetime.date.today(),party='')

    def test_bad_date(self):
        response = self.client.get(self.uri +'?date=not_a_date')
        self.assert_400(response)

    def test_party_param(self):
        response = self.client.get(self.uri + '?party=M')

        data.data.gender_json.assert_called_with(date=datetime.date.today(),party='M')

    def test_no_party(self):
        response = self.client.get(self.uri + '?party=')

        data.data.gender_json.assert_called_with(date=datetime.date.today(),party='')

    def test_bad_party(self):
        response = self.client.get(self.uri + '?party=not-a-pary-abbr')
        self.assert_400(response)

class TestRoutesDataParliamentJson(TestCase):
    def create_app(self):
        return create_app(testing=True)

    @classmethod
    def setUpClass(cls):
        cls.uri = '/data/parliament.json'

        data.data.parliament_json = Mock(return_value=dict(data=[{'test': 1}]))
        data.data.get_parties = Mock(return_value=['M'])

    def setUp(self):
        pass
        
    def test_simple_query(self):
        response = self.client.get(self.uri)
        self.assert_200(response)

    def test_date_param(self):
        str_date = '2014-01-01'
        #test that it works with a param
        self.client.get(self.uri + '?date=' + str_date)
        date = datetime.datetime.strptime('2014-01-01', '%Y-%m-%d').date()
        data.data.parliament_json.assert_called_with(date=date)

    def test_no_date(self):
        self.client.get(self.uri)
        data.data.parliament_json.assert_called_with(date=datetime.date.today())

    def test_bad_date(self):
        response = self.client.get(self.uri + '?date=not_a_date')
        self.assert_400(response)