import os
from flask.ext.testing import TestCase
from unittest.mock import MagicMock

from demokratikollen.www.app import create_app

class TestRoutes(TestCase):

    def create_app(self):
        return create_app(testing=True)

    #Gender routing:
    def test_gender_json_200(self):
        response = self.client.get('/data/gender.json')
        self.assert_200(response)

    def test_gender_json_params(self):
    	from demokratikollen.www.app.controllers import data
    	from datetime import date as d
    	data.gender_json = MagicMock(return_value="Hello World")
    	date = '2014-01-01'

    	#test that it works with a param
    	self.client.get('/data/gender.json?date=' + date)
    	data.gender_json.assert_called_with(date=date)

    	#Test that it works without.
    	self.client.get('/data/gender.json')
    	data.gender_json.assert_called_with(date=d.today().isoformat())


