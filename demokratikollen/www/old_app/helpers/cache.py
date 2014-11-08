from flask.ext.cache import Cache
import os
# Setup the Cache
cache = Cache(config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': str(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) + '/cache'})
