# -*- coding: utf-8 -*-
from demokratikollen.core.db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased, joinedload
import os
import psycopg2 as pg
from progress_bar import InitBar
import pickle
#import PIL.Image as Image
import colorsys
import math
from demokratikollen.core.utils import misc as misc_utils, postgres as pg_utils, mongo_utils as mongo_utils

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d

def create_covoting_matrix(session, member_map):
    n_members = len(member_map)

    covoting_matrix = []
    for i in range(n_members):
        covoting_matrix.append([])
        for j in range(n_members):
            covoting_matrix[i].append({'vote_equal': 0, 'vote_different': 0})
    
    num_polls = s.query(Poll).count()

    pbar = InitBar(title="Parsing Votes")
    pbar(0)
    
    for i, poll_id in enumerate(s.query(Poll.id)):
        votes = s.query(Vote).filter(Vote.poll_id == poll_id).filter(Vote.vote_option != 'Frånvarande').all()
        for vote1 in votes:
            for vote2 in votes:
                if vote1.member_id in member_map and vote2.member_id in member_map:
                    if vote1.vote_option == vote2.vote_option:
                        covoting_matrix[member_map[vote1.member_id]][member_map[vote2.member_id]]['vote_equal'] += 1
                    else:
                        covoting_matrix[member_map[vote1.member_id]][member_map[vote2.member_id]]['vote_different'] += 1
                            
        pbar((100.0*i)/num_polls)
    return covoting_matrix
    
def get_active_members(session, vote_cutoff=1):
    members = []

    q = s.query(Member, func.count(Vote.id),Party.abbr).join(Member.votes).join(Member.appointments).join(Party)\
                                            .filter(ChamberAppointment.start_date > datetime.date(2010,1,1))\
                                            .group_by(Member.id, Party.abbr)\
                                            .order_by(Party.abbr)
    for i, member in enumerate(q.all()):
        if member[1] > vote_cutoff:
            members.append({ "member": row2dict(member[0]), "party_abbr": member[2]})
    return members

def get_data(session, datastore,load=True, vote_cutoff=1):
    
    if load:
        #load matrix and membermap
        covoting_matrix = datastore.get_object('covoting_matrix')
        member_map = datastore.get_object('member_map')
        members = datastore.get_object('members')
    else:
        print("Getting member list")
        members = get_active_members(s,50)
        datastore.store_object(members, 'members')
        n_members = len(members)
        print("Number of members: " + str(n_members))

        #create member map
        member_map = {}
        for i, member_dict in enumerate(members):
            print(member_dict['member'])
            member_map[member_dict['member']['id']] = i
        datastore.store_object(member_map, 'member_map')

        covoting_matrix = create_covoting_matrix(session, member_map)
        datastore.store_object(covoting_matrix, 'covoting_matrix')
                    
    return members, member_map, covoting_matrix


# Connect to SQLAlchemy db and create structure
engine = create_engine(pg_utils.engine_url())

session = sessionmaker()
session.configure(bind=engine)
s = session()

datastore = mongo_utils.mongo_utilsDatastore()

if misc_utils.yes_or_no("Do you want to get data from the database again?"):
    members, member_map, covoting_matrix = get_data(s,datastore,False)
else:
    members, member_map, covoting_matrix = get_data(s,datastore)

for member in members:
    print(member['member'])

abbr_color = {'M': colorsys.rgb_to_hls(32/256,76/256,212/256), \
                          'C': colorsys.rgb_to_hls(0/256,153/256,68/256), \
                          'FP': colorsys.rgb_to_hls(98/256,184/256,231/256), \
                          'KD': colorsys.rgb_to_hls(38/256,27/256,114/256), \
                          'MP': colorsys.rgb_to_hls(119/256,207/256,86/256), \
                          'S': colorsys.rgb_to_hls(247/256,17/256,39/256), \
                          'SD': colorsys.rgb_to_hls(220/256,220/256,74/256), \
                          'V': colorsys.rgb_to_hls(182/256,0/256,9/256) }
                                  

