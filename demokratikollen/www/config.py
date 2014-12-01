import os
import multiprocessing

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = multiprocessing.cpu_count() * 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
if 'CSRF_SESSION_KEY' in os.environ:
	CSRF_SESSION_KEY = os.environ['CSRF_SESSION_KEY']
else:
	CSRF_SESSION_KEY = "=4ay95k7zib1a42@v28ni4v9vf$4b85+=jft8!29&#xdd#cp&="

# Secret key for signing cookies
if 'SECRET_KEY' in os.environ:
	SECRET_KEY = os.environ['SECRET_KEY']
else:
	SECREY_KEY = "=4ay95k7zib1a42@v28ni4v9vf$4b85+=jft8!29&#xdd#cp&="