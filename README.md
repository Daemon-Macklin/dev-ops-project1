# AWS instance manager

#### What is it?
This program allows users to start aws instances do some basic management

### Creating an instance
There are three things required to create an AWS instance:
* A security Group ID which allows ssh and http trafic from anywhere.
* A keypair that was made with your AWS account.
* A name that will be used for the instance tags.

The user will be prompted to provide all of these in the program.
Once all of the required data is collect an instance will be created and the
User will have to wait 60 seconds before they can continue.


The instance will be created and a userdata script will be run which will
update, install nginx and state an nginx webserver on the instance. 


### Checking nginx 
Provided with the run_webserver.py script is a check_webserver.py script.
using secure copy(scp) the check_webserver.py script is copied to the instance
of the users choice, after it is copied up the script has it's permissions 
changed so that it can be run and then it is run. The script will check if the
nginx server is running, using ps and grep and if it is will inform the user and if it is not
running it will try and start the nginx server.


### Starting s3 bucket
There is only one thing required to start an s3 bucket.
* A name for the bucket

The user will be prompted to provide this information and once given a bucket 
will be created and a list of the users buckets will be printed out


### Uploading an image to server
There are two steps in this process
1. Uploading the selected image to the selected bucket
2. Congifuring the nginx server on a selected instance to display the image

In the first step the user is prompted with a list of all their buckets
Then the user is asked to provide the name of the bucket they want to use.
Once the user selects the bucket name the user is prompted for the name
of the image file they want to upload. With the bucket name and the file
name it is possible to upload the image to the bucket


In the second step the user is prompted with a list of all their instances 
and asked to input the id of the instance they want to use to host the 
image. Once selected the user must provided the key they used to create the
instance. The html is generated with the bucket name and file name that was
input earlier to generate the link to the image. Then this html is echoed into
an index.html file. This index.html file is then secure copied up to the 
instance in the location of the nginx default index.html file.


### Terminate Instance
When this option is selected the user is prompeted with a list of their
instances. The user is asked to provide the id of the intstance they want
to terminate and if the id is correct the instance is terminated.


### List Instance
When this option is selected the programme goes through each instance
and prints some basic information about the instance and if the instance
is running the user will be asked if they want system information. If the user
inputs 1 some ssh commands will be run which will return cpu usage, a list
of the running processes and virtual memory stats. 


### Terminate Bucket
When this option is selected the user is prompeted with a list of their 
buckets. The user is asked to provide the name of the bucket they want 
to terminate and if the name is correct the bucket is terminated if the
bucket is empty.


### Empty Bucket
When this option is selected the user is prompeted with a list of their
buckets. The user is asked to provide the name of the bucket they want
to empty and if the name is correct the bucket is emptied.


### List buckets
When this option is selected a list of buckets is outputted to the user


