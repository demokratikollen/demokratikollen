import os
from flask.ext.testing import TestCase
from unittest.mock import MagicMock
from mock import patch

from demokratikollen.www.app import create_app
from demokratikollen.www.app.mod_static import controllers

class TestRoutes(TestCase):

    def create_app(self):
        return create_app(testing=True)

    #Check some basic stuff for the index route.
    def test_route_index(self):
        response = self.client.get('/')
        self.assert_200(response)
        self.assert_context('header_home_class', 'active')
        self.assertTemplateUsed('/static/index.html')

    def test_route_contact(self):
        response = self.client.get('/kontakt')
        self.assert_200(response)
        self.assert_context('header_contact_class','active')
        self.assertTemplateUsed('/static/contact.html')



    