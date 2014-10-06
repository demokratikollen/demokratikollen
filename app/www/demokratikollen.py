from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_structure import *
import os
import utils

#config
DATBASE_URL = os.environ['DATABASE_URL']
DEBUG = True
SECRET_KEY = '=4ay95k7zib1a42@v28ni4v9vf$4b85+=jft8!29&#xdd#cp&='

app = Flask(__name__)
app.config.from_object(__name__)

def create_db_session():
    engine = create_engine(utils.engine_url())
    session = sessionmaker()
    session.configure(bind=engine)
    return session()

def get_db_session():
     session = getattr(g, 'db_session', None)
     if session is not None:
         return session

@app.before_request
def before_request():
    g.db_session = create_db_session()

@app.teardown_request
def teardown_request(exception):
    session = getattr(g, 'db_session', None)
    if session is not None:
        session.close()

@app.route('/member/<int:member_id>', methods=['GET'])
def member(member_id):
    s = get_db_session()
    member = s.query(Member).filter(Member.id == member_id).one()
    
    output = str(member) + "<br> Uppdrag:<br>"
    output += "<ul>"
    
    for ap in member.appointments:
        output += "<li>{}: {} -> {}</li>".format(ap.classtype, ap.start_date, ap.end_date)
    
    output += "</ul>"
    return output
    
@app.route('/member', methods=['GET'])
def member_all():
    s = get_db_session()
    members = s.query(Member).all()
    output = ""
    for member in members:
        output += "{}: {}<br>".format(member.id, member)
    return output

if __name__ == '__main__':
    app.debug = DEBUG
    app.run()
