demokratikollen
===============

## Installation using Virtualbox, Vagrant and Ansible (Unix/Mac OS)

1. Download and install Virtualbox: https://www.virtualbox.org/wiki/Downloads
2. Download and Install Vagrant: https://www.vagrantup.com/downloads.html 
3. Install Ansible: `sudo apt-get install ansible`

## Installation using Virtualbox, Vagrant and Ansible (Windows)

1. Download and install Virtualbox: https://www.virtualbox.org/wiki/Downloads
2. Download and install Vagrant: https://www.vagrantup.com/downloads.html 
3. Download and install Git (needed for cmd-line ssh): http://git-scm.com/

## Starting the virtual machine

Assumes you have cloned the repository.

1. In the root of the repository, run `vagrant up`
2. Once completed, run `vagrant ssh` to login to the VM. The app code is residing in ~/demokratikollen. The ~/demokratikollen folder on the guest machine is shared with the app folder in the repository on the host machine.

Refresh the provisioning: `vagrant provision`
Graceful shutdown of the vm: `vagrant halt`
Remove the vm: `vagrant destroy`

## Import data into the database

The data is first imported into the ``riksdagen`` database using cleaned up SQL files from data.riksdagen.se. Then it is transformed into SQLAlchemy. All necessary steps to import the data are contained in ~/demokratikollen/do_import.sh.

In the VM (vagrant ssh),

1. Go to the application root: `cd ~/demokratikollen`
2. Run

        ./do_import.sh

This command will download and import data from Riksdagen. The command takes several hours on a standard PC. See the contents of do_import.sh for details.

## Calculations

Some datasets for the webapp are produced by lengthy calculations. All such calculations reside in ~/demokratikollen/calculations, and will be run once at deploy. Results are typically stored in the MongoDB.

In your development environment you must run these scripts manually before starting the webapp.

## The Flask webapp
In order to run the flask app, ssh to the VM and run `gunicorn_debug` or `gunicorn_debug_nocache` to disable caching (see below). The server can be accessed from the host machine by accessing http://127.0.0.1:5000. 

The Flask app is not served directly but goes through a proxy server. The gunicorn instance listens for connections locally on port 8000 while an nginx instance listens to connections on port 5000 which is port forwarded to the host machine. The nginx instance serves static content and forwards other requests to the gunicorn instance.

### Caching of pages in the webapp 
Caching is enabled for the Flask app. Caching is done by importing the cache
module with `from ...app.helpers.cache import cache` and using the decorators
`@cache.cached(int timeout in seconds)` and `@cache.memoize(int timeout in
seconds)` on any method. The `cached` decorator should be used for methods
without arguments while the `memoize` decorator should be used for methods
with arguments.

Although there are some speedups the main benefit of caching methods in the
webapp is to keep the database interactions down. Full caching will probably
be done at the nginx level if that should ever be needed.

## MongoDB Datastore
To use the datastore add `from demokratikollen.core.utils.mongodb import MongoDBDatastore` and create a new datastore object as `ds = MongoDBDatastore()`. 
In order to save an object in the datastore call the `store_object(object[any], identifier[string])` method which saves the object in the database. Subsequent calls with the same identifier should overwrite the object. Retrieve objects with the `get_object(identifier)` method. 

The class should be able to store any python object. Storing sqlalchemy objects work but they loose the connection with the session so relationships do not work on retrieved objects. Perhaps there is a way to restore the connection, but for now serialize the data into a dictionary.

## Front-end compilation and dependency handling
[Gulp](http://gulpjs.com/) is used to compile SASS style sheets, concatenate and minify JS and CSS dependencies, and to copy necessary files (fonts, images, etc.) to the right places.

To run, go to the folder `~/demokratikollen/www/design` and run `gulp all` or run any of the specialized tasks defined in `gulpfile.js` (in the same folder). To modify/add tasks or change dependencies, edit `gulpfile.js`.

To install `npm` packages and add as dependencies go to `~/` and run `npm install <pkg> --save-dev`. The file `~/package.json` is linked to the corresponding file in `~demokratikollen/www/design`, which is tracked in `git`.
