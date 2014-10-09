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
1. Go to the riksdagen sql folder: `cd ~/app/riksdagen_sql`
2. Download the data: `python get_data.py`
3. Clear database: `./clear_db.sh`
4. Initialize database: `./init_db.sh`

## Import of data to ORM database
First initialize database according to instructions above. Then run `python ~/app/populate_orm.py`.

## Running the Flask webapp
Open an ssh to the VM and change dir to `~/app/www` and run `gunicorn_debug app:app`. The server can be accessed from the host machine by accessing http://127.0.0.1:5000.

## Running tests for the webapp
Open an ssh to the VM and change dir to `~/app/www` and run `behave`. If it seems to fail, it might be that the last webserver instance was not closed. If so, run `killall gunicorn` and try again.
