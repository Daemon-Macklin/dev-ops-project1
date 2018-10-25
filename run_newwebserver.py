#!/usr/bin/python3

#Author Daemon Macklin
import subprocess
import boto3
import time
ec2 = boto3.resource('ec2')
s3 = boto3.resource("s3")


#Method to display and handle main menu user choice
def mainMenu():
 print("----------------------------------------------------------")
 print("Please select an option:")
 print("1) Create instance")
 print("2) Check nginx")
 print("3) Start S3 bucket")
 print("4) Upload image to server")
 print("5) Terminate Instance")
 print("6) Terminate Bucket")
 print("7) List Instances")
 print("8) List Buckets")
 print("9) Empty Bucket")
 
 option =-1
 
 #looping until the program gets a valid input
 while 1:
  option = input("Please select an option >")
  try:
      
  #Try catch to ensure input is a number
   option = int(option)
   
   #If the input is valid break 
   if(option > 0 and option < 10):
    break
  except:
   print("Please input a number")
  print("Invalid option")
 options[option]()


#Method to start instance and install/start nginx server
def instanceInstall():
 created=False
 print("Starting Instance")
 
 #Getting user input for instance tag
 name = input("Please enter the name of the instance you want to create >")
 nameTag = {'Key':'Name', 'Value' : name}
 
 #Getting name of the .pem key the user wants to create the instance with
 keyNameDefault="DaemonMacklin1225"
 keyName = input("Please enter the name of your key (Please leave out .pem)["+keyNameDefault+"] >")
 if(keyName == ""):
     keyName = keyNameDefault
     
 #If the Key has a .pem get rid of it
 if(keyName[-4:]== ".pem"):
     keyName = keyName[:-4]
 print("Key Name: ", keyName)
 
 #Getting the id of the security group for the instance
 securityGroupDefault='sg-05c0f69ea9cacbb26'
 securityGroup = input("Please enter the name of your key (Please leave out .pem)["+securityGroupDefault+"] >")
 if(securityGroup == ""):
     securityGroup = securityGroupDefault
 print("Security Group: ", securityGroup)
 try:
     
  #Creating the instance
  instance = ec2.create_instances(
   ImageId='ami-0c21ae4a3bd190229',
   MinCount=1,
   MaxCount=1,
   InstanceType='t2.micro',
   SecurityGroupIds=[securityGroup],
   KeyName=keyName,
   UserData='''
    #!/bin/bash
    sudo yum -y update
    sudo yum -y install python3
    sudo amazon-linux-extras install nginx1.12 -y
    sudo service nginx start
    chkconfig nginx on'''
   )

  #Adding the tags to the instance
  instance[0].create_tags(Tags=[nameTag])
  print("An Instance with ID", instance[0].id, "Has been created")

  #Waiting until the instance has been created
  x=0
  while (x < 100):
   print("Please wait.... Booting instance")
   x = x + 10
   time.sleep(6)
 except Exception as e:
  print("Error Starting instance", e)

 #returning to the main menau
 mainMenu()


#Method to start bucket start
def createBucket():
    print("Starting Bucket")

    #Getting the user input of the name of the bucket
    bucket_name = input("What would you like to name your bucket? >")
    bucket_name = bucket_name.lower()
    try:

        #Creating the bucket
        response = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})

        #Making the bucket public
        response.Acl().put(ACL='public-read')
        print(response)
    except Exception as error:
        print(error)

    #Displaying all the buckets
    for bucket in s3.buckets.all():
      print (bucket.name)
      print ("----------------------------------------------------------")
    try:

     #Printing items inside the bucket if the user has access
     for item in bucket.objects.all():
          print ("\t%s" % item.key)
        
    except:
          print("Access Denied")
              
    mainMenu()


#Method to upload image to the bucket and display it on the server    
def uploadImage():
    print("Upload Image")

    #Displying all the buckets
    for bucket in s3.buckets.all():
     print (bucket.name)
     print ("----------------------------------------------------------")
    try:

     #Displaying all the itmes in the bucket
     for item in bucket.objects.all():
          print ("\t%s" % item.key)
        
    except:
          print("Access Denied")
    uploaded=False

    #Getting the name of the bucket the user wants to use
    bucket_name = input("What is the name of the bucket you want to upload an image to >")

    #Getting the image the user wants to upload
    object_name = input("what is the name of the image file you want to upload, please include the extension >")
    try:

     #Putting the image in the bucket and making it public
     response = s3.Object(bucket_name, object_name).put(Body=open(object_name, 'rb'),  ACL='public-read')

     #response.Acl().put(ACL='public-read')
     print (response)
     uploaded=True
    except Exception as error:
     print (error)

    #If the upload succeded then do this
    if uploaded is True:

        #Displaying all the instances
        for instance in ec2.instances.all():
            print(instance.id, instance.state, instance.tags)
            print("----------------------------------------------------------")

        #Getting the id of the instance the user wants to use
        instanceID = input("What is the id of the instance you want to use >")
        for instance in ec2.instances.all():

            #If the ID the user input is this instance id do this
            if(instanceID == instance.id):
                print("In Instance: ", instanceID)

                #Getting the ipaddress of the instance
                instanceIp = instance.public_ip_address

                #Getting the key used for the instance
                keyName = input("Please enter the name of the key used for this instance (Please leave out .pem) >")

                #If the key has the .pem extention get rid of it
                if(keyName[-4:]== ".pem"):
                 keyName = keyName[:-4]
                print(keyName)
                message = input("What message would you like to display with your picture?")

                #Making the html code to upload the the index.html
                html ='<html><h1>'+message+'</h1><img src="https://s3-eu-west-1.amazonaws.com/'+bucket_name+'/'+object_name+'"></img></html>'

                #Putting the html code into an index.html file
                echoCommand="echo '"+html+"' > index.html"
                subprocess.run(echoCommand, check=True, shell=True)

                #ssh command to change html file so that it can be changed
                sshSetOpenPermissions = "ssh -t -o StrictHostKeyChecking=no -i "+ keyName +".pem ec2-user@" + instanceIp + " 'cd /usr/share/nginx/html/ ;sudo chmod 777 index.html '"

                #Scp command to upload the index.html file to the instance and replace the exsisting index file with the new one
                scpCommand = "scp -i "+ keyName +".pem index.html ec2-user@"+ instanceIp +":/usr/share/nginx/html/index.html"

                #ssh command to change html file to be read only
                sshSetClosePermissions = "ssh -t -o StrictHostKeyChecking=no -i "+ keyName +".pem ec2-user@" + instanceIp + " 'cd /usr/share/nginx/html ;sudo chmod 444 index.html '"

                try:

                #running the command
                    subprocess.run(sshSetOpenPermissions, check=True, shell=True)
                    subprocess.run(scpCommand,check=True, shell=True)
                    subprocess.run(sshSetClosePermissions,check=True, shell=True)
                    print("Image can now be viewed at: " , instanceIp)
                except Exception as e:
                    print(e)
                break
    mainMenu()


#Method to upload check_webserver.py file to instance and run it
def checkNginx():
    print("Check Nginx")

    #Printing out all the instances
    for instance in ec2.instances.all():
     print (instance.id, instance.state, instance.tags)
     print("----------------------------------------------------------")

    #Getting all the instance ids 
    instanceID = input("What is the id of the instance you want to check? >")
    for instance in ec2.instances.all():

     #If the user give id is this instances id then do this
     if(instance.id == instanceID):
      print("in Instance", instanceID)

      #Get the ip address of the instance
      instanceIp = instance.public_ip_address
      print("IP address = " + instanceIp)

      #Get the key the user used for this instance
      keyName = input("Please enter the name of the key you used for this instance (Please leave out .pem) >")

      #If the key has the .pem extention get rid of it
      if(keyName[-4:]== ".pem"):
        keyName = keyName[:-4]
      print(keyName)

      try:

       #ssh command to ensure first time connection will work
       sshCommand = "ssh -t -o StrictHostKeyChecking=no -i "+ keyName +".pem ec2-user@" + instanceIp + " 'pwd'"
       subprocess.run(sshCommand,check=True, shell=True)

       #scp command to copy the script to the instacne with the ip instanceIp
       scpCommand = "scp -i "+ keyName +".pem check_webserver.py ec2-user@"+ instanceIp +":."
       print(scpCommand)
       subprocess.run(scpCommand,check=True, shell=True)
       print("Check webserver script sucessfully copied to instnace")
      except Exception as e:
       print(e)

      try:

       #ssh command to give the file execute permissions and then run the file
       sshCommand = "ssh -t -o StrictHostKeyChecking=no -i "+ keyName +".pem ec2-user@" + instanceIp + " 'sudo chmod +x check_webserver.py; ./check_webserver.py'"
       print(sshCommand)
       subprocess.run( sshCommand,check=True, shell=True)
      except Exception as e:
          print(e)
          print("Incorrect Key")
      break
    mainMenu()

    
#Method to terminate instance    
def terminateInstance():
    print("Terminating Instance")

    #Loop through instances
    for instance in ec2.instances.all():
        print(instance.id, instance.state, instance.tags)

    #Let user input id of the instance they want to delete
    instanceID = input("Which instance would you like to terminate >")
    for instance in ec2.instances.all():
        if(instance.id == instanceID):
            #Terminate the instance
            response = instance.terminate()
            print(response)
    
    mainMenu()

    
#Method to list instances
def listInstances():
    print("Listing Instances")

    #Looping though instances
    for instance in ec2.instances.all():

        #Printing out basic data
        print("InstanceId -> ",instance.id)
        print("Instance State -> ",instance.state)
        print("Instance Tags -> ",instance.tags)
        print("Instance Ip address ->" ,instance.public_ip_address)
        print("Instance DNS name ->", instance.public_dns_name)

        #Asking use if they want data that would require an ssh command to get
        instanceIp = instance.public_ip_address
        instanceState = instance.state
        if(instanceState["Name"] == "running"):
          print("1) Yes")
          print("2) No")
          option=input("Would you like system data for this instance >")
          if(option == "1"):

            #Getting the name of the key for the instance
            keyName=input("Please enter the name of the key you used for this instance (Please leave out .pem) >")
            if(keyName[-4:]== ".pem"):
              keyName = keyName[:-4]
            print("Key Name: ", keyName)

            #Making commands for getting cpu usage, running process and the virtual memory stats
            cpuCheck = """grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage "%"}'"""
            cpuCommand = "ssh -t -o StrictHostKeyChecking=no -i "+ keyName +".pem ec2-user@" + instanceIp + " "+cpuCheck+""
            psCommand = "ssh -t -o StrictHostKeyChecking=no -i "+ keyName +".pem ec2-user@" + instanceIp + " 'ps'"
            vmstatCommand = "ssh -t -o StrictHostKeyChecking=no -i "+ keyName +".pem ec2-user@" + instanceIp + " 'vmstat'"
            try:

               #Running the commands and displaying the data
               subprocess.run(cpuCommand, check=True, shell=True)
               print("CPU usage")
               print("----------------------------------------------------------")
               subprocess.run(psCommand, check=True, shell=True)
               print("Processes running")
               print("----------------------------------------------------------")
               subprocess.run(vmstatCommand, check=True, shell=True)
               print("Virtual Memory Stats")
               print("----------------------------------------------------------")
               print("End of data")
             
            except Exception as e:
               print(e)
        elif(instanceState["Name"] == "terminated"):
          print("Cannot get System data as instance is terminated")
        elif(instanceState["Name"] == "shutting-down"):
            print("Cannot get System data as instance is shutting")
        print ("----------------------------------------------------------")  
    mainMenu()
    

#Method to list buckets
def listBuckets():
    print("List buckets")

    #Displying all the buckets
    for bucket in s3.buckets.all():
     print (bucket.name)
     print ("----------------------------------------------------------")
    try:

     #Displaying all the itmes in the bucket
     for item in bucket.objects.all():
          print(item.key)
    except:
     print("Access Denied")
    mainMenu()  

def emptyBucket():
    print("Empty Bucket")

    #Displying all the buckets
    for bucket in s3.buckets.all():
     print (bucket.name)
     print ("----------------------------------------------------------")
    try:

     #Displaying all the itmes in the bucket
     for item in bucket.objects.all():
          print(item.key)
    except:
     print("Access Denied")

    #user input name of the bucket they want to empty
    bucketName = input("What is the name of the bucket you want to empty >")
    for bucket in s3.buckets.all():
     if(bucket.name == bucketName):
         for key in bucket.objects.all():
           try:
             #Remove the items from bucket
             response = key.delete()
             print (response)
           except Exception as error:
             print (error)
    
    mainMenu()    
    
def terminateBucket():
    print("Terminating Bucket")

    #Displying all the buckets
    for bucket in s3.buckets.all():
     print (bucket.name)
     print ("----------------------------------------------------------")
    try:

     #Displaying all the itmes in the bucket
     for item in bucket.objects.all():
          print("\t%s" % item.key)
    except:
     print("Access Denied")

    #user input name of the bucket they want to empty
    bucketName = input("What is the name of the bucket you want to delete >")
    for bucket in s3.buckets.all():
     if(bucket.name == bucketName):
         try:
           #Delete bucket
           response = bucket.delete()
           print (response)
         except Exception as error:
           print (error)
    
    mainMenu()

    
#Dict of methods or menu
options = {1 : instanceInstall, 2: checkNginx, 3: createBucket, 4: uploadImage, 5: terminateInstance, 6: terminateBucket, 7: listInstances, 8: listBuckets, 9: emptyBucket}


#Starting program
if __name__ == '__main__':
  mainMenu()
