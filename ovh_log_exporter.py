#!/usr/bin/env python3
# coding: utf8

import requests as requests
import re as regex
from os import path
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from configparser import ConfigParser
import json, ovh, csv, os.path, smtplib, datetime


today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

#Create required sub-directories
if os.path.exists("log") == False:
    os.mkdir("log")

if os.path.exists("csv") == False:
    os.mkdir("csv")

#log/Logs_OVH_DD_MM_AAA.log
logfile = "log/Logs_OVH_"+today.strftime("%d_%m_%Y")+".log"

#Log text with [DATE - TIME] format, print it and save it to file
def log(text):
    now = datetime.datetime.now()
    current_time = now.strftime("%d/%m/%Y - %H:%M:%S")
    log_data = "["+current_time+"] "+text
    f = open(logfile, "a+", encoding="utf-8")
    f.write(log_data+"\n")
    f.close()
    print(log_data)


#Check if config.ini exist or leave
if os.path.exists("config.ini"):
    parser = ConfigParser()
    parser.read('config.ini')
else:
    log("Error, no config.ini found, exiting")
    exit()

#Check if configuration is okay

config_tree={'OVH':["endpoint", "application_key", "application_secret", "consumer_key", "service_name"], "MAIL":["username", "password", "server", "port", "receivers"]}


for section in config_tree:
    if parser.has_section(section) == False:
        log(" /!\\ Missing "+section+" section /!\\")
        exit()
    for i in range(len(config_tree[section])):
        if parser.has_option(section, config_tree[section][i]) == False:
            log(" /!\\ Missing "+section+":"+config_tree[section][i]+" /!\\")
            exit()
        else:
            if parser.get(section, config_tree[section][i]) == "":
                log(" /!\\ "+section+":"+config_tree[section][i]+" empty /!\\")
                exit()

ovh_endpoint=parser.get("OVH", "endpoint")
ovh_application_key=parser.get("OVH", "application_key")
ovh_application_secret=parser.get("OVH", "application_secret")
ovh_consumer_key=parser.get("OVH", "consumer_key")
service_name=parser.get("OVH", "service_name")

mailusername=parser.get("MAIL", "username")
mailpassword=parser.get("MAIL", "password")
mailserver=parser.get("MAIL", "server")
mailport=parser.get("MAIL", "port")
email_receivers=parser.get("MAIL", "receivers").split(", ")



ovh_client = ovh.Client(
    endpoint=ovh_endpoint,               # Endpoint of API OVH Europe (List of available endpoints)
    application_key=ovh_application_key,    # Application Key
    application_secret=ovh_application_secret, # Application Secret
    consumer_key=ovh_consumer_key,       # Consumer Key
)


#csv/Logs_OVH_DD_MM_AAA.csv
filename = "csv/Logs_OVH_"+today.strftime("%d_%m_%Y")+".csv"

#csv/Logs_OVH_DD_MM_AAA.csv DD = Current Day -1
last_day_filename = "csv/Logs_OVH_"+yesterday.strftime("%d_%m_%Y")+".csv"



#Coresp between list index and dict key
index_name_corresp = {"taskId":0, "name":1, "type":2, "progress":3, "description":4, "parentTaskId":5, "createdFrom":6, "createdBy":7, "executionDate":8, "endDate":9, "lastModificationDate":10}

#Final List header
tasks_list = [["Reference", "Name", "Type", "Progress", "Comment", "Affected Service", "Created from", "Created by:", "Start", "End", "Update"]]

#Get all tasks through API
pcc_tasks = ovh_client.get('/dedicatedCloud/'+service_name+'/task/')

#Mailer VARS
email_subject = "OVH log export for "+today.strftime("%d/%m/%Y")
email_masquerade = "OVH Log Export Bot <"+mailusername+">"

#increment
total_tasks_count = 0

#Return csv as splitted list
def get_file(filename):
    file = open(filename, "r", encoding="utf-8")
    lines = file.read().splitlines()
    file.close()
    content_as_list=[]
    for i in range(len(lines)):
        if len(lines[i]) > 0:
            content_as_list.append(lines[i].split(";"))
    return content_as_list

#Append new_file between old_file[0] nad old_file[1] and write it to filename
def update_file(filename, old_file, new_file):
    old_content = []
    for i in range(len(old_file)):
        old_content.append(";".join(old_file[i]))

    new_content = []
    new_file.reverse()
    new_file.insert(0, new_file.pop())

    for j in range(len(new_file)):
        new_content.append(";".join(new_file[j]))

    file = open(filename, "w+",  encoding="utf-8-sig")
    file.write("\n".join(new_content)+"\n")
    file.write("\n".join(old_content[1:]))
    file.close();


#Gather old tasks ids that are successfull
def get_ended_ids(filename):
    result = []
    if (path.exists(filename)):
        file = open(filename, "r", encoding="utf-8")
        content_as_list = file.read().splitlines()
        file.close()
        for i in range(len(content_as_list)):
            line_splited = content_as_list[i].split(";")
            if line_splited[index_name_corresp['progress']] == "100" and i > 0:
                result.append(line_splited[index_name_corresp["taskId"]])
    return result

#Convert OVH date format to more readeable one
def date_converter(date):
    if date != None :
        year=date[:4]
        month=date[5:7]
        day=date[8:10]
        hour=date[11:13]
        min=date[14:16]
        sec=date[17:19]
        return str(day)+"/"+str(month)+"/"+str(year)+" - "+str(hour)+":"+str(min)+":"+str(sec)
    else :
        return "";




ended_ids = get_ended_ids(last_day_filename);

#Gather last day .csv
if os.path.exists(last_day_filename):
    last_day_file =  get_file(last_day_filename)
else:
    last_day_file = [""]

old_file = last_day_file

log("")
log(" --- "+today.strftime("%d/%m/%Y")+" ---")
log("(Total tasks: "+str(len(pcc_tasks)-1)+")")
log("")

#For all tasks id
for i in range(len(pcc_tasks)):
    task_id = pcc_tasks[i]

    #Intermediate saving
    if(len(tasks_list)) > 20:
        log("Writting "+str(len(tasks_list)-1)+" tasks to file")
        update_file(filename, old_file, tasks_list)
        tasks_list = [tasks_list[0]]
        old_file = get_file(filename)

    #If task not already ended yesterday
    if str(task_id) not in ended_ids:
        #Get Task details
        try:
            task = ovh_client.get('/dedicatedCloud/'+service_name+'/task/'+str(task_id))


            #If task updated today or yesterday
            if (date_converter(task['lastModificationDate'])[:10] == today.strftime("%d/%m/%Y")) or (date_converter(task['lastModificationDate'])[:10] == yesterday.strftime("%d/%m/%Y")):  
                log("Adding task "+str(task_id))
                total_tasks_count += 1

                #Add Description to task depending on content
                task_description = ""
                if task['parentTaskId'] !=  None:
                    task_description += " Task: "+str(task['parentTaskId'])
                if task['networkAccessId'] != None:
                    task_description += " Datacenter: "+str(task['networkAccessId'])
                if task['hostId'] != None:
                    task_description += " Host: "+str(task['hostId'])
                if task['userId'] != None:
                    task_description += " User: "+str(task['userId'])

                #Create task as lsit from API data
                task_as_list = [str(task['taskId']),str(task['name']), str(task['type']), str(task['progress']), str(task_description), str(task['parentTaskId']), str(task['createdFrom']), str(task['createdBy']), date_converter(task['executionDate']), date_converter(task['endDate']), date_converter(task['lastModificationDate'])]
                tasks_list.append(task_as_list.copy());
            else:
                print(str(task_id)+" too old")
        except ovh.exceptions.ResourceNotFoundError :
        	print("Error: Task "+str(task_id)+" not found")
    else:
         print(str(task_id)+" already completed")
#put last element (header) on top of list

log(" -- Recap : Added "+str(total_tasks_count)+" tasks")

#save file
update_file(filename, old_file, tasks_list)

msg=MIMEMultipart()
msg['From'] = email_masquerade
msg['To'] = ",".join(email_receivers)
msg['Subject'] = email_subject


mailbody = "OVH Log export on "+service_name+" done,\nResults attached to this mail.\n\n\nLogs:\n"+''.join(open(logfile, "r", encoding="utf-8").readlines())

msg.attach(MIMEText(mailbody,'text'))


attachment = open(filename, "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename[4:])

msg.attach(part)

mailcontent=msg.as_string()

server = smtplib.SMTP(mailserver, mailport)
server.starttls()
server.login(mailusername, mailpassword)
server.sendmail(mailusername,email_receivers, mailcontent)
server.quit()
