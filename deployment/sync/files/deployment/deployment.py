#!/bin/python

import logger
import steps

# Get a logger.
log = logger.get_logger()

base_dir = '/home/wercker/'

#The first step is to check if stuff have changed. If something changed all database images has to be replaced.
files_changed = steps.verify_changes(base_dir, log)

#Depending on what changed. create new containers and start them.
steps.create_images(base_dir, log, files_changed)
steps.create_containers(base_dir, log, files_changed)
steps.remove_containers(base_dir, log, files_changed)
steps.remove_images(base_dir, log, files_changed)
steps.post_deployment(base_dir,log)