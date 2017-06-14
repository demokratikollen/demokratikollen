from selenium import webdriver
import subprocess
import os
import shlex
import time

def before_all(context):
    print("Starting Webserver and Webdriver")
    context.server = subprocess.Popen(shlex.split("gunicorn --debug -b 127.0.0.1:8000 demokratikollen.www.gunicorn_no_cache:app"),stdout=subprocess.PIPE)
    context.driver = webdriver.PhantomJS()

def after_all(context):
    print("Stopping the Webserver and Webdriver")
    context.driver.quit()
    context.server.terminate()
    out,err = context.server.communicate()
    print("Output from the webserver:")
    print(out)

def after_step(context, step):
    if 'BEHAVE_DEBUG_ON_ERROR' in os.environ and step.status == "failed":
        # -- ENTER DEBUGGER: Zoom in on failure location.
        # NOTE: Use IPython debugger, same for pdb (basic python debugger).
        import ipdb
        ipdb.post_mortem(step.exc_traceback)
