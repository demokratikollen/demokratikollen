import os
from flask.ext.testing import TestCase
from unittest.mock import MagicMock

from demokratikollen.www.app import create_app
from demokratikollen.www.app.controllers import data

class TestGenderJson(TestCase):

    def create_app(self):
        return create_app(testing=True)