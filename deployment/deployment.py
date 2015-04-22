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



 # Get a logger.
logger.setup_logging(base_dir)
log = logging.getLogger(__name__)

with open(os.path.join(base_dir,'demokratikollen/deployment/deploy.conf'),'r') as df:
    deploy_extent = df.readline()
    deploy_extent = deploy_extent[:-1]

#The first step is to check if stuff have changed. If something changed all database images has to be replaced.
files_changed = steps.verify_changes(base_dir, log)

deploy_settings = dict(base_dir=base_dir, log=log, files_changed=files_changed, deploy_extent=deploy_extent)
log.info(deploy_settings)

steps.pre_deployment(deploy_settings)

try:
    #Depending on what changed. create new containers and start them.
    steps.create_images(deploy_settings)
    # steps.create_containers(deploy_settings)
    # steps.start_containers(deploy_settings)

    # log.info("Waiting 30 seconds for things to boot")
    # time.sleep(30)

    # if deploy_extent != 'SRC' and files_changed:
    # 	steps.populate_riksdagen(deploy_settings)
    # 	steps.populate_orm(deploy_settings)
    # 	steps.run_calculations(deploy_settings)

    # steps.switch_nginx_servers(deploy_settings)
    # steps.remove_containers(deploy_settings)
    # steps.remove_images(deploy_settings)
    #steps.post_deployment(deploy_settings)

    os.remove(lock_file)
except Exception as e:
    #steps.remove_current_images_and_containers(deploy_settings)
    steps.clean_up_after_error(deploy_settings)
    log.error("Something went wrong during deployment. Check logs, fix error, tidy up, remove lock file and try again")
    #log.error(e)
