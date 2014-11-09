from demokratikollen.www.app import app
from selenium import webdriver
import subprocess
import os
import shlex


def before_all(context):
   print("Starting Webserver and Webdriver")
   os.environ["TESTING"] = "1"
   context.server = subprocess.Popen(shlex.split("gunicorn --debug -b 127.0.0.1:5555 demokratikollen.www.app:app"),stdout=subprocess.PIPE)
   context.driver = webdriver.PhantomJS()
   context.app = app
   #fulhack
   

def after_all(context):
   print("Stopping the Webserver and Webdriver")
   context.driver.quit()
   context.server.terminate()
   out,err = context.server.communicate()
   print("Output from the webserver:")
   print(out)

   del os.environ["TESTING"]
