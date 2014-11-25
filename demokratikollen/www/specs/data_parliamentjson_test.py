import os
from datetime import date
from flask.ext.testing import TestCase
from unittest.mock import MagicMock

from demokratikollen.www.app.helpers.db import db, Member
from demokratikollen.www.app import create_app
from demokratikollen.www.app.models import data

d = date(2014,1,1)

class TestGenderJson(TestCase):

    def create_app(self):
        return create_app(testing=True)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_calls_data_routine_correctly(self):
        data.get_parliament_db_statement = MagicMock()

        response = data.parliament_json(date=d)

        data.get_parliament_db_statement.assert_called_with(d)

    def test_sets_correct_stats(self):
        out_data = [(1,'S'),(2,'MP'),(3,'V')]

        data.get_parliament_db_statement = MagicMock()
        cursor = data.get_parliament_db_statement.return_value
        cursor.all.return_value = out_data

        response = data.parliament_json(date=d)

        self.assertEqual(len(response['data']), 3 )
        self.assertEqual(response['statistics']['n_members'], 3)

    def test_sets_data_correctly(self):
        out_data = [(1,'S'),(2,'MP'),(3,'V')]

        data.get_parliament_db_statement = MagicMock()
        cursor = data.get_parliament_db_statement.return_value
        cursor.all.return_value = out_data

        response = data.parliament_json(date=d)

        sorted_on_member_id_data = sorted(response['data'], key=lambda k: k['member_id'])

        for i, datum in enumerate(sorted_on_member_id_data):
            self.assertEqual(datum['member_id'], out_data[i][0])

    def test_sorts_data_correctly(self):
        out_data = [(1,'S'),(2,'MP'),(3,'V')]

        data.get_parliament_db_statement = MagicMock()
        cursor = data.get_parliament_db_statement.return_value
        cursor.all.return_value = out_data

        response = data.parliament_json(date=d)

        correct_order = [2,1,3]

        for i, datum in enumerate(response['data']):
            self.assertEqual(datum['member_id'], correct_order[i])

