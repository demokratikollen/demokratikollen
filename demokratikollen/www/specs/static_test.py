import demokratikollen.www.app as demo
from nose.tools import *

class TestStatic:

    @classmethod
    def setup_class(self):
        demo.app.config['TESTING'] = True
        self.demo = demo.app.test_client()

    @classmethod
    def teardown_class(self):
        print("quitting...")

    #Check if all members route works.
    def test_route_basic(self):
        response = self.demo.get('/')
        eq_(response.status_code, 200)
    def test_route_indexed(self):
        response = self.demo.get('/kontakt')
        eq_(response.status_code, 200)

