# -*- coding: utf-8 -*-

# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
from demokratikollen.www.app.helpers.cache import cache
from demokratikollen.www.app.helpers.db import db
from demokratikollen.core.db_structure import Member, ChamberAppointment

def index():
    return render_template("/index.html")

def parliament():
    return render_template("/parliament/index.html")

def parties():
    return render_template("/parties/index.html")

def issues():
    return render_template("/issues/index.html")

def about():
    return render_template("/about.html")