#!/bin/python

import logger
import logging
import steps
import time
import os
import sys

base_dir = '/home/wercker/'
lock_file = os.path.join(base_dir, 'deploy.lock')
# Check if the lockfile exists
if os.os.path.isfile(lock_file):
    print("Lockfile exists. Either a deploy is running or the last deploy failed somehow. Exiting...")
    sys.exit(1)
else:
    #touch lockfile
    with open(lock_file, 'a'):
        os.utime(lock_file, None)

# Start demonizing
pid = os.fork()

if pid != 0:
    sys.exit(0)

os.chdir('/')
os.setsid() 
os.umask(0)

pid = os.fork()
if pid != 0:
    print("Forking...Watch deployment.log for logging")
    sys.exit(0)



 # Get a logger.
logger.setup_logging(base_dir)
log = logging.getLogger(__name__)

#The first step is to check if stuff have changed. If something changed all database images has to be replaced.
files_changed = steps.verify_changes(base_dir, log)

#Depending on what changed. create new containers and start them.
steps.create_images(base_dir, log, files_changed)
steps.create_containers(base_dir, log, files_changed)
steps.start_containers(base_dir, log, files_changed)

log.info("Waiting 30 seconds for things to boot")
time.sleep(30)

steps.populate_riksdagen(base_dir, log)
steps.populate_orm(base_dir,log)
steps.run_calculations(base_dir,log)

steps.switch_nginx_servers(base_dir,log)
steps.remove_containers(base_dir, log, files_changed)
steps.remove_images(base_dir, log, files_changed)
steps.post_deployment(base_dir,log)

#Remove lock_file
os.remove(lock_file)