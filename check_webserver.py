#!/usr/bin/python3

"""A tiny Python program to check that nginx is running.
Try running this program from the command line like this:
  python3 check_webserver.py
"""

import subprocess

def checknginx():
  try:

    #Command that lists process and filters out ones with nginx in them
    cmd = 'ps -A | grep nginx'

    #Running the command
    subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Nginx Server IS running")
    #Returning 0 indecating the server is running
    return 0
   
  except subprocess.CalledProcessError:
    print("Nginx Server IS NOT running")
    #Returning 1 indecating the server is not running
    return 1

def startnginx():
  try:
    
    #Command that starts nginx
    cmd = 'sudo service nginx start'

    #Running command
    subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Nginx started")
   
  except subprocess.CalledProcessError:

    #If the command doesn't run return there is an error
    print("--- Error starting Nginx! ---")
    
# Define a main() function.
def main():

    #If the checknginx function returns run, run the start nginx function
    if checknginx() == 1:
      startnginx()
      
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()

