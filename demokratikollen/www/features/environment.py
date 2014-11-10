from selenium import webdriver
import subprocess
import os
import shlex


def before_all(context):
   print("Starting Webserver and Webdriver")
   context.server = subprocess.Popen(shlex.split("gunicorn --debug -b 127.0.0.1:5555 demokratikollen.www.gunicorn_testing:app"),stdout=subprocess.PIPE)
   context.driver = webdriver.PhantomJS()
   #fulhack
   

def after_all(context):
   print("Stopping the Webserver and Webdriver")
   context.driver.quit()
   context.server.terminate()
   out,err = context.server.communicate()
   print("Output from the webserver:")
   print(out)