# -*- coding: utf-8 -*-
from db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased, joinedload
import utils
import os
import psycopg2 as pg
from progress_bar import InitBar
import pickle
import PIL.Image as Image
import colorsys
import math

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
            members.append({ "member": member[0], "party_abbr": member[2]})
    return members

def get_data(session,load=True, vote_cutoff=1):
    
    if load:
        #load matrix and membermap
        with open('covoting_data/covoting_matrix', 'rb') as f:
            covoting_matrix = pickle.load(f)
        with open('covoting_data/member_map', 'rb') as f:
            member_map = pickle.load(f)
        with open('covoting_data/members', 'rb') as f:
            members = pickle.load(f)
    else:
        print("Getting member list")
        members = get_active_members(s,50)
        n_members = len(members)
        print("Number of members: " + str(n_members))

        #create member map
        member_map = {}
        for i, member_dict in enumerate(members):
            member_map[member_dict['member'].id] = i

        covoting_matrix = create_covoting_matrix(session, member_map)

        #save matrix and membermap
        with open('covoting_data/covoting_matrix', 'wb') as f:
            pickle.dump(covoting_matrix, f)
        with open('covoting_data/member_map', 'wb') as f:
            pickle.dump(member_map, f)
        with open('covoting_data/members', 'wb') as f:
            pickle.dump(members,f)
            
    return members, member_map, covoting_matrix


# Connect to SQLAlchemy db and create structure
engine = create_engine(utils.engine_url())

session = sessionmaker()
session.configure(bind=engine)
s = session()

if utils.yes_or_no("Do you want to get data from the database again?"):
    members, member_map, covoting_matrix = get_data(s,False)
else:
    members, member_map, covoting_matrix = get_data(s)

n_members = len(members)

abbr_color = {'M': colorsys.rgb_to_hls(32/256,76/256,212/256), \
                          'C': colorsys.rgb_to_hls(0/256,153/256,68/256), \
                          'FP': colorsys.rgb_to_hls(98/256,184/256,231/256), \
                          'KD': colorsys.rgb_to_hls(38/256,27/256,114/256), \
                          'MP': colorsys.rgb_to_hls(119/256,207/256,86/256), \
                          'S': colorsys.rgb_to_hls(247/256,17/256,39/256), \
                          'SD': colorsys.rgb_to_hls(220/256,220/256,74/256), \
                          'V': colorsys.rgb_to_hls(182/256,0/256,9/256) }


img_together = Image.new('RGB', (n_members,n_members), "black")
pixels_together = img_together.load()
img_different = Image.new('RGB', (n_members,n_members), "black")
pixels_different = img_different.load()

for i,row in enumerate(covoting_matrix):
    for j,column in enumerate(row):
        #print(str(column['vote_equal']) + " " + str(column['vote_different']))
        if column['vote_equal']+column['vote_different'] > 0:
            party_abbr = members[i]['party_abbr']
                
            if party_abbr in abbr_color:
                current_abbr_color = abbr_color[party_abbr]
            else:
                current_abbr_color = colorsys.rgb_to_hls(0,0,0)
            
            fraction_together = column['vote_equal']/(column['vote_equal']+column['vote_different'])
            
            log_fraction_together = 0.01*10**(1+fraction_together)
            
            r, g, b = colorsys.hls_to_rgb(current_abbr_color[0],log_fraction_together,current_abbr_color[2])
            pixels_together[i,j] = (int(r*255),int(g*255),int(b*255))
            r, g, b = colorsys.hls_to_rgb(current_abbr_color[0],1 - log_fraction_together,current_abbr_color[2])
            pixels_different[i,j] = (int(r*255),int(g*255),int(b*255))
            
            
img_together = img_together.rotate(90)
img_together.save('figs/covoting-together.png')            

img_different = img_different.rotate(90)
img_different.save('figs/covoting-different.png')            

