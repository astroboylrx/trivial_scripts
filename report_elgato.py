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
    server.set_debuglevel(0)
    text = msg.as_string()
    server.sendmail(FROM, TO, text)
    server.quit()
    print "Message Sent."
    return

def split_jobs(bjobs):
    jobs_dict = []
    if bjobs == "No unfinished job found\n":
        return jobs_dict
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
        email_body = "Job(s) done (or killed):\n"
        for count, item in enumerate(c):
            email_body += ' '.join([original_jobs[item]['JOBID'], original_jobs[item]['JOB_NAME']])+'\n'
        original_jobs = [item for item in original_jobs if original_jobs.index(item) not in c]
    else:
        email_body = "NULL"

    c = np.where(now_jobs_new == 1)[0]
    if len(c) != 0:
        email_body = "Job(s) added:\n"
        for count2, item2, in enumerate(c):
            original_jobs.append(now_jobs[item2])
            email_body += ' '.join([now_jobs[item2]['JOBID'], now_jobs[item2]['JOB_NAME']])+'\n'
    return now_jobs, original_jobs, email_body

def check_unsubmitted_jobs(filepath, n_to_submit):
    with open(filepath) as unsubmitted_jobs_file:
        unsubmitted_jobs_path = unsubmitted_jobs_file.read().splitlines()
    jobs_path = [x for x in unsubmitted_jobs_path if len(x) != 0]
    unsubmitted_jobs_path = [x for x in unsubmitted_jobs_path if len(x) != 0 and x[0] != '#']        
        
    if len(unsubmitted_jobs_path) != 0:
        if len(unsubmitted_jobs_path) < n_to_submit:
            n_to_submit = len(unsubmitted_jobs_path)
        for count in range(n_to_submit):
            cmd = "/bin/bash /home/u5/rixin/bin/pysub_jobs "
            cmd = cmd + unsubmitted_jobs_path[count]
            print cmd
            bsub = subprocess.call(shlex.split(cmd), stderr=subprocess.STDOUT)
            for count2, item in enumerate(jobs_path):
                if item == unsubmitted_jobs_path[count]:
                    jobs_path[count2] = '#'+jobs_path[count2]
                    break
            #unsubmitted_jobs_path[count] = '#'+unsubmitted_jobs_path[count]
        #del unsubmitted_jobs_path[0:n_to_submit] # n_to_submit is not included

        all_jobs = '\n'.join(jobs_path)
        jobs_file = open(filepath, "w")
        jobs_file.write(all_jobs)
        jobs_file.close()

        return len(unsubmitted_jobs_path)-n_to_submit
    return 0
        
    


# main function, if you call this as main function
if __name__ == '__main__':

    # dealing with arguments
    import argparse
    parser = argparse.ArgumentParser(description="This is an script to submit and monitor multiple jobs.")
    parser.add_argument('-p', '--path', dest="path", help="Path of a file which contains lsf.sh files (default: /home/u5/rixin/runs/kkruns/jobs2run.txt)", default="/home/u5/rixin/runs/kkruns/jobs2run.txt")
    parser.add_argument('-n', '--njobs', dest="njobs", help="Maximum number of running jobs (default: 3)", type=int, default=3)
    parser.add_argument('-e', '--email', dest="email", help="If set, then job monitor will send email to report status", action='store_const', const=True, default=False)
    parser.add_argument('-c', '--comment', dest="comment", help="Subject post-comment for emails", default="default")
    args = parser.parse_args()

    bjobs = subprocess.check_output("bjobs", stderr=subprocess.STDOUT)
    original_jobs = split_jobs(bjobs)
    if len(original_jobs) < args.njobs:
        jobs_left = check_unsubmitted_jobs(args.path, args.njobs-len(original_jobs))
        print "jobs_left = ", jobs_left    

    # main loop
    bjobs = subprocess.check_output("bjobs", stderr=subprocess.STDOUT)
    if bjobs == "No unfinished job found\n":
        if args.email:
            send_to_myself(bjobs+args.comment+current_datetime_string(), bjobs)
    else:
        if args.email:
            send_to_myself("Job-Monitor launching "+args.comment+current_datetime_string(), bjobs)
        original_jobs = split_jobs(bjobs)
        time.sleep(30)
        bjobs = subprocess.check_output("bjobs", stderr=subprocess.STDOUT)
        while bjobs != "No unfinished job found\n" or jobs_left != 0:
            now_jobs = split_jobs(bjobs)
            now_jobs, original_jobs, email_body = compare_jobs(now_jobs, original_jobs)
            if email_body == "NULL":
                time.sleep(30)
            else:
                if len(now_jobs) < args.njobs:
                    jobs_left = check_unsubmitted_jobs(args.path, args.njobs-len(now_jobs))
                    print "jobs_left = ", jobs_left
                if args.email:
                    send_to_myself("Job-Monitor update "+args.comment+current_datetime_string(), email_body)
            bjobs = subprocess.check_output("bjobs", stderr=subprocess.STDOUT)
            
        email_body = "Job(s) done (or killed):\n"
        for count in range(len(original_jobs)):
            email_body += ' '.join([original_jobs[0]['JOBID'], original_jobs[0]['JOB_NAME']])+"\n"
            del original_jobs[0]
        if args.email:
            send_to_myself("Job-Monitor done "+args.comment+current_datetime_string(), email_body)
        
        
    
    
