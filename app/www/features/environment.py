from app import app
import liveandletdie
from selenium import webdriver
#import threading
import subprocess
import shlex


def before_all(context):
   print("Starting Webserver and Webdriver")
   context.server = subprocess.Popen(shlex.split("gunicorn --debug -b 127.0.0.1:5555 app:app"),stdout=subprocess.PIPE)
   context.driver = webdriver.PhantomJS()
   context.app = app
   #fulhack
   

def after_all(context):
   print("Stopping the Webserver and Webdriver")
   context.driver.quit()
   context.server.terminate()
