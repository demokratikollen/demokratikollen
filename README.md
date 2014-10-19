demokratikollen
===============

## Installation using Virtualbox, Vagrant and Ansible (Unix/Mac OS)

Assumes you have cloned the repository.

1. Download and install Virtualbox: https://www.virtualbox.org/wiki/Downloads
2. Download and Install Vagrant: https://www.vagrantup.com/downloads.html 
3. Install Ansible: `sudo apt-get install ansible`
4. In the root of the repository, run `vagrant up`
5. Once completed, run `vagrant ssh` to login to the VM. The app code is residing in ~/app. The ~/app folder on the guest machine is shared with the app folder in the repository on the host machine.

## Installation using Virtualbox, Vagrant and Ansible (Windows)
Assumes you have cloned the repository.

1. Download and install Virtualbox: https://www.virtualbox.org/wiki/Downloads
2. Download and install Vagrant: https://www.vagrantup.com/downloads.html 
3. Download and install Git (needed for cmd-line ssh): http://git-scm.com/
4. In the root of the repository, run `vagrant up` (The Ansible step can take some time and will not output logs until finished)
5. Once completed, run `vagrant ssh` to login to the VM. The app code is residing in ~/app. The ~/app folder on the guest machine is shared with the app folder in the repository on the host machine.

## Initialization of riksdagen database
1. Go to the application root: `cd ~/demokratikollen`

2. Clear any contents of the database and create tables:

        python import_data.py wipe

3. Download data from the parliament's website:

        python import_data.py download data/urls.txt data/download

4. Unpack all the zipped data files:

        python import_data.py unpack data/download data/download

5. Clean errors so files can be imported. The flag `--remove` removes the unpacked source files after successful cleanup.

        python import_data.py clean data/download data/cleaned --remove

6. Execute all INSERT statements found in the cleaned data files:

        python import_data.py execute data/cleaned


### Adding more data to riksdagen database

When/if you download more data and want to add it, you can of course work with single files:

1. Just add the new url to `~/demokratikollen/data/urls.txt`. The download command by default skips downloading files that already exist.

2. Then run something like this:

        python import_data.py download data/download
        python import_data.py unpack data/download/my_new_file_name.sql.zip
        python import_data.py clean data/download/my_new_file_name.sql.zip data/cleaned
        python import_data.py execute data/cleaned/cleaned_my_new_file_name.sql

## Import of data to ORM database
First initialize database according to instructions above. Then run `python ~/app/populate_orm.py`.

## The Flask webapp
In order to run the flask app, ssh to the VM and run `gunicorn_debug`. The server can be accessed from the host machine by accessing http://127.0.0.1:5000. 

The Flask app is not served directly but goes through a proxy server. The gunicorn instance listens for connections locally on port 8000 while an nginx instance listens to connections on port 5000 which is port forwarded to the host machine. The nginx instance serves static content and forwards other requests to the gunicorn instance.

### Structure in the webapp 
The structure of the webapp is loosely based on the tutorial from
[Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-structure-large-flask-applications). 
For general usages of Flask, the [quick start](http://flask.pocoo.org/docs/0.10/quickstart/) on their homepage 
is a good source of information. Logically separated parts of the app are located in their own folders in the app
dir. In each `controller.py` file, the code for the routes associated with the module is defined.
If needed, a `model.py` file can contain model-like behavior for the module. Each module is
defined as a Flask Blueprint in the `controller.py` file and registered in the apps `__init__.py`
file located in the root of the app dir. Templates for each module need to be located in a folder with the 
same name as the module in the templates folder. The master layout in `layout.html` defines should be used as 
a parent for module templates.

## MongoDB Datastore
To use the datastore add `from utils.mongodb import MongoDBDatastore` and create a new datastore object as `ds = MongoDBDatastore()`. 
In order to save an object in the datastore call the `store_object(object[any], identifier[string])` method which saves the object in the database. Subsequent calls with the same identifier should overwrite the object. Retrieve objects with the `get_object(identifier)` method. 

The class should be able to store any python object. Storing sqlalchemy objects work but they loose the connection with the session so relationships do not work on retrieved objects. Perhaps there is a way to restore the connection, but for now serialize the data into a dictionary.
