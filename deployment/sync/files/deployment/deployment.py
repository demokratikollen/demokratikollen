#!/bin/python

import logger
import steps
import time
import os
import sys

pid = os.fork()


if pid != 0:
	print("Forking...Watch deployment.log for logging")
	sys.exit(0)

os.chdir('/')
os.setsid() 
os.umask(0)

pid = os.fork()
if pid != 0:
	print("Forking...Watch deployment.log for logging")
	sys.exit(0)


base_dir = '/home/wercker/'

# Get a logger.
log = logger.get_logger(base_dir)

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