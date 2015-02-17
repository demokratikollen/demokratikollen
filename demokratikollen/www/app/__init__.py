# Import flask and template operators
from flask import Flask, request,render_template, redirect
import os
from urllib.parse import urlparse, urlunparse

import datetime
from flask.ext.jsontools import DynamicJSONEncoder

#import helpers
from demokratikollen.www.app.helpers.cache import cache, httpdate
from demokratikollen.www.app.helpers.db import db

import demokratikollen.www.app.views.data.member
import demokratikollen.www.app.views.data.parliament
import demokratikollen.www.app.views.data.parties
import demokratikollen.www.app.views.pages
from demokratikollen.www.app import views


class ApiJSONEncoder(DynamicJSONEncoder):
    def default(self, o):
        # Custom formats
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, datetime.date):
            return o.isoformat()
        if isinstance(o, set):
            return list(o)

        return o.__json__()
        # Fallback
        return super(DynamicJSONEncoder, self).default(o)

#App Factory to facilitate testing.
def create_app(testing=False, caching=True):
    app = Flask(__name__, static_url_path='', static_folder='static')

    #Load the basic config.
    app.config.from_object('demokratikollen.www.config')

    app.json_encoder = ApiJSONEncoder

    #If we require testing. change some configs.
    if testing:
        print("Running Test env.")
        app.config['TESTING'] = True
        cache.config['CACHE_TYPE'] = 'null'

    if not caching:
        cache.config['CACHE_TYPE'] = 'null'
    else:
        # Add a 1 day expiry on all responses.
        @app.after_request
        def expiration_header(response):
            if not 'Expires' in response.headers:
                response.headers['Expires'] = httpdate(datetime.datetime.now() + datetime.timedelta(days=1))
            return response

    #init the cache
    cache.init_app(app)

    #inti the db
    db.init_app(app)

    # 404 error handling
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    # Add a redirect for urls no being www
    @app.before_request
    def redirect_nonwww():
        """Redirect non-www requests to www."""
        urlparts = urlparse(request.url)
        print(urlparts)
        if urlparts.netloc == 'demokratikollen.se':
            urlparts_list = list(urlparts)
            urlparts_list[1] = 'www.demokratikollen.se'
            return redirect(urlunparse(urlparts_list), code=301)

    # Import a module / component using its blueprint handler variable

    blueprints = (
        views.data.parliament.blueprint,
        views.data.member.blueprint,
        views.data.parties.blueprint,
        views.pages.blueprint)

    # Register blueprint(s)
    for b in blueprints:
        app.register_blueprint(b)

    return app








