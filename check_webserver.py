#!/usr/bin/python3

"""A tiny Python program to check that nginx is running.
Try running this program from the command line like this:
  python3 check_webserver.py
"""

import subprocess

def checknginx():
  try:
    cmd = 'ps -A | grep nginx'
   
    subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Nginx Server IS running")
    return 0
   
  except subprocess.CalledProcessError:
    print("Nginx Server IS NOT running")
    return 1

def startnginx():
  try:
    cmd = 'sudo service nginx start'
    subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Nginx started")
   
  except subprocess.CalledProcessError:
    print("--- Error starting Nginx! ---")
    
# Define a main() function.
def main():
    if checknginx() == 1:
      startnginx()
      
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()

