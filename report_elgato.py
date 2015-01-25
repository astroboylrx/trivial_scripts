#!/usr/bin/env python
#

import subprocess, os, smtplib, shlex, time, datetime
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
            if count == 1:
                del jobs[count][-3]
            temp_dict = dict(zip(keys, jobs[count]))
            jobs_dict.append(temp_dict)
            count += 1
    return jobs_dict
    
def current_datetime_string():
    return datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")


# main function, if you call this as main function
if __name__ == '__main__':
    bjobs = subprocess.check_output("bjobs", stderr=subprocess.STDOUT)
    if bjobs == "No unfinished job found\n":
        send_to_myself(bjobs, bjobs)
    else:
        send_to_myself("Job-Monitor launching "+current_datetime_string(), bjobs)
        original_jobs = split_jobs(bjobs)
        time.sleep(3)
        bjobs = subprocess.check_output("bjobs", stderr=subprocess.STDOUT)
        while bjobs != "No unfinished job found\n":
            now_jobs = split_jobs(bjobs)
            n_jobs_done = len(original_jobs) - len(now_jobs)
            if n_jobs_done == 0:
                time.sleep(3)
            else:
                email_body = "Job(s) done:\n"
                for count in range(n_jobs_done):
                    email_body += ' '.join([original_jobs[0]['JOBID'], original_jobs[0]['JOB_NAME']])+"\n"
                    del original_jobs[0]
                send_to_myself("Job-Monitor update "+current_datetime_string(), email_body)
            bjobs = subprocess.check_output("bjobs", stderr=subprocess.STDOUT)
            print 'new loop'
        email_body = "Job(s) done:\n"
        for count in range(len(original_jobs)):
            email_body += ' '.join([original_jobs[0]['JOBID'], original_jobs[0]['JOB_NAME']])+"\n"
            del original_jobs[0]
        send_to_myself("Job-Monitor done "+current_datetime_string(), email_body)
        
        
    
    
