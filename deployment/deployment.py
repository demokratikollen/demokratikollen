#!/bin/python

import logger
import logging
import steps
import time
import os
import sys
import re

base_dir = '/home/deploy/'
lock_file = os.path.join(base_dir, 'deploy.lock')
# Check if the lockfile exists
if os.path.isfile(lock_file):
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


override = True

 # Get a logger.
logger.setup_logging(base_dir)
log = logging.getLogger(__name__)

with open(os.path.join(base_dir,'demokratikollen/deployment/deploy.conf'),'r') as df:
    deploy_extent = df.readline()
    deploy_extent = deploy_extent[:-1]

#The first step is to check if stuff have changed. If something changed all database images has to be replaced.
files_changed = steps.verify_changes(base_dir, log)

redo_calculations = override or (deploy_extent.lower() in ['all', 'calculations'] and files_changed)

deploy_settings = dict(base_dir=base_dir, log=log, userid=os.getuid(), files_changed=files_changed, redo_calculations=redo_calculations)
log.info(deploy_settings)

steps.pre_deployment(deploy_settings)

try:
    #Depending on what changed. create new containers and start them.
    log.info("Building images.")
    steps.create_images(deploy_settings)

    if redo_calculations:
        log.info("Setting up containers for populating databases.")
        steps.setup_containers_for_calculations(deploy_settings)
        log.info("Populating riksdagen-database.")
        steps.populate_riksdagen(deploy_settings)
        log.info("Populating demokratikollen-ORM")
        steps.populate_orm(deploy_settings)
        log.info("Running calculations.")
        steps.run_calculations(deploy_settings)
        log.info("Saving databases.")
        steps.save_database_data(deploy_settings)
        log.info("Cleaning up after database population.")
        steps.stop_and_remove_temp_containers(deploy_settings)

    log.info("Stopping and removing current containers.")
    steps.stop_and_remove_current_containers(deploy_settings)

    log.info("Creating and starting data containers (if needed)")
    steps.create_and_start_data_containers(deploy_settings)

    log.info("Updating the webapp to newest source.")
    steps.update_webapp_src(deploy_settings)

    log.info("Creating and starting app containers.")
    steps.create_and_start_app_containers(deploy_settings)

    log.info("Waiting 60 seconds for services to boot")
    time.sleep(60)

    if redo_calculations:
        log.info("Updating the databases.")
        steps.update_database_data(deploy_settings)
    
    log.info("Running post deployment clean up.")
    steps.post_deployment(deploy_settings)
    
    log.info("Removing lockfile.")
    os.remove(lock_file)
except Exception as e:
    steps.clean_up_after_error(deploy_settings)
    log.error("Something went wrong during deployment. Check logs, fix error, tidy up, remove lock file and try again")
    log.error(e)
