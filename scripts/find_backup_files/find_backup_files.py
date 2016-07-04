#Tests all files and sees if any backups of them have remained on the webserver.
#For example, myapp.php will become backup.myapp.php, myapp.php.backup, myapp.backup, etc.
#HTTPS NOT SUPPORTED

#SETTINGS:

#If you want to test only php filenames
onlyPHP = False

#HEAD requests are faster, GET requests are less suspicious.
#mode = "GET"
mode = "HEAD"

#The extensions you want to test
#Edge cases - "Copy of" before and "~" after
backupExtensions = ["", "zip", "bak", "txt", "src", "dev", "old", "inc", "orig", "copy", "cpy", "tmp", "bkup", "backup", "tar", "gz"] #Should make custom handling for zip, tar and gz files, since index.zip.php doesn't really make any sense.

import urllib2
import httplib
import sys
import traceback


def bruteforce(targetFile, position, mode):
	#Separate the domain
	targetRoot = targetFile.split("/")[0]
	#Separate the filename from the directory name
	separatedBySlashes = targetFile.split("/")
	targetFilename = separatedBySlashes[-1]
	if onlyPHP:
		if "php" not in targetFilename and "PHP" not in targetFilename and "php5" not in targetFilename and "php4" not in targetFilename and "php3" not in targetFilename:
			return
			
	#Separate the file path
	if len(separatedBySlashes[1:-1]) == 0:
		targetFilePath = "/"
	else:
		targetFilePath = "/" + "/".join(separatedBySlashes[1:-1]) + "/" 

	#old.filename.php	
	if position == "before":
		testFilename = backupExtension + "." + targetFilename
	#filename.php.old
	elif position == "after":
		testFilename = targetFilename + "." + backupExtension
	#filename.old.php
	elif position == "between":
		testFilename = targetFilename.split(".")[0] + "." + backupExtension + "." + ".".join(targetFilename.split(".")[1:])
	#filename.old
	elif position == "replace":
		if backupExtension == "":
			testFilename = targetFilename.split(".")[0]
		else:
			testFilename = targetFilename.split(".")[0] + "." + backupExtension
	#filename.php~
	elif position == "~":
		testFilename = targetFilename + "~"
	#Copy of filename.php
	#Url encoding is necessary.
	elif position == "copyof":
		testFilename = "Copy%20of%20" + targetFilename
	try:
		#print targetRoot + targetFilePath + testFilename
		print("Testing: " + targetRoot + targetFilePath + testFilename)
		conn = httplib.HTTPConnection(targetRoot)
		#print(targetRoot)
		conn.request(mode, targetFilePath + testFilename)
		#print(mode+ ", " + targetFilePath + testFilename)
		response = conn.getresponse()
		#Will not display if urllib throws 404 error
		if "404" not in str(response.status):
			if response.reason == "":
				print("[ERROR]: DISCARDING, RESPONSE CODE EMPTY. This might mean the request is malformed.")
				return
			foundBackups.append(targetFilePath + testFilename + ": " + str(response.status) + " " + response.reason)

	except Exception:
		exception = traceback.format_exc()
		print exception
	
		

#You should put the lowest level directory that you're trying to attack here.
#targetRoot= "www.turundustugi.ee"#"127.0.0.1"
#put specific directories and filenames here.
#targetFiles = ["/web-serveur/ch17/index.php"]#/hello.php"]
#Get the filepaths from filelist.txt instead
filelist = open("filelist.txt", "r")
targetFiles = filelist.readlines()
targetFiles = [path.strip() for path in targetFiles] #Take away the \n
targetFiles = [path.replace("http://", "") for path in targetFiles] #Remove the http:// and https://
#HTTPS CURRENTLY NOT SUPPORTED!!!!!!
#targetFiles = [path.replace("https//", "") for path in targetFiles] 

foundBackups = []






for targetFile in targetFiles:
	#Edge cases first, since they don't require checking all extensions:
	bruteforce(targetFile, "~", mode)
	bruteforce(targetFile, "copyof", mode)
	
	for backupExtension in backupExtensions:
		#Try putting it before the filename
		bruteforce(targetFile, "before", mode)
		#After
		bruteforce(targetFile, "after", mode)
		#Between the filename and the extension
		bruteforce(targetFile, "between", mode)
		#Instead of
		bruteforce(targetFile, "replace", mode)
	
print("\n\nResults:")
for backup in foundBackups:
	print(backup)
