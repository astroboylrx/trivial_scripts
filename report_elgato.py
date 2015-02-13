#!/usr/bin/env python
#

import subprocess, os, smtplib, shlex, time, datetime
import numpy as np
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def send_to_myself(Subject, body):
    # email options
    SERVER = "localhost"
    FROM = "rixin@elgato-login.hpc.arizona.edu"
    TO = ["rixin@email.arizona.edu"]

    msg = MIMEMultipart()
    msg['From'] = FROM
    msg['To'] = ", ".join(TO)
    msg['Subject'] = Subject

    #body = "Python test mail"
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SERVER)
    server.set_debuglevel(1)
    text = msg.as_string()
    server.sendmail(FROM, TO, text)
    server.quit()

def split_jobs(bjobs):
    jobs_dict = []
    if bjobs == "No unfinished job found\n":
        return bjobs_dict
    jobs = bjobs.split('\n')
    keys = jobs[0].split()
    del keys[-3]
    count = 1
    while count < len(jobs):
        if len(jobs[count]) == 0 or jobs[count][0] == ' ':
            del jobs[count]            
        else:
            jobs[count] = jobs[count].split()
            jobs[count].append(' '.join(jobs[count][-3:]))
            del jobs[count][-4:-1]
            if len(jobs[count]) == 8:
                del jobs[count][-3]
            temp_dict = dict(zip(keys, jobs[count]))
            jobs_dict.append(temp_dict)
            count += 1
    return jobs_dict
    
def current_datetime_string():
    return datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")

def compare_jobs(now_jobs, original_jobs):
    original_jobs_exist = np.zeros(len(original_jobs))
    now_jobs_new = np.zeros(len(now_jobs))
    for count, item in enumerate(now_jobs):
        new_job = 1
        for count2, item2 in enumerate(original_jobs):
            if item['JOBID'] == item2['JOBID']:
                original_jobs_exist[count2] = 1
                new_job = 0
                break;
        if new_job == 1:
            now_jobs_new[count] = 1
    c = np.where(original_jobs_exist==0)[0]
    if len(c) != 0:
        print "jobs done or killed"
        email_body = "Job(s) done (or killed):\n"
        for count, item in enumerate(c):
            email_body += ' '.join([original_jobs[item]['JOBID'], original_jobs[item]['JOB_NAME']])+"\n"
        original_jobs = [item for item in original_jobs if original_jobs.index(item) not in c]
    else:
        email_body = "NULL"

    c = np.where(now_jobs_new == 1)[0]
    if len(c) != 0:
        print "adding new jobs"
        for count2, item2, in enumerate(c):
            original_jobs.append(now_jobs[item2])
    return now_jobs, original_jobs, email_body
            
# main function, if you call this as main function
if __name__ == '__main__':
    bjobs = subprocess.check_output("bjobs", stderr=subprocess.STDOUT)
    if bjobs == "No unfinished job found\n":
        send_to_myself(bjobs, bjobs)
    else:
        send_to_myself("Job-Monitor launching "+current_datetime_string(), bjobs)
        original_jobs = split_jobs(bjobs)
        time.sleep(30)
        bjobs = subprocess.check_output("bjobs", stderr=subprocess.STDOUT)
        while bjobs != "No unfinished job found\n":
            print "New Loop"
            now_jobs = split_jobs(bjobs)
            now_jobs, original_jobs, email_body = compare_jobs(now_jobs, original_jobs)
            if email_body == "NULL":
                time.sleep(30)
            else:
                send_to_myself("Job-Monitor update "+current_datetime_string(), email_body)
            bjobs = subprocess.check_output("bjobs", stderr=subprocess.STDOUT)
        email_body = "Job(s) done (or killed):\n"
        for count in range(len(original_jobs)):
            email_body += ' '.join([original_jobs[0]['JOBID'], original_jobs[0]['JOB_NAME']])+"\n"
            del original_jobs[0]
        send_to_myself("Job-Monitor done "+current_datetime_string(), email_body)
        
        
    
    
