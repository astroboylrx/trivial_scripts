#!/usr/bin/env python
# This is job monitor on El Gato
#

import subprocess, sys, os, smtplib, shlex, time, datetime
import numpy as np
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def current_datetime_string():
    return datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")

def send_to_myself(Subject, body):
    # email options
    SERVER = "localhost"
    FROM = "rixin@elgato-login.hpc.arizona.edu"
    TO = ["rixin@email.arizona.edu"]

    msg = MIMEMultipart()
    msg['From'] = FROM
    msg['To'] = ", ".join(TO)
    msg['Subject'] = Subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SERVER)
    server.set_debuglevel(0)
    text = msg.as_string()
    server.sendmail(FROM, TO, text)
    server.quit()
    print("Message Sent.")
    return

class Job:
    def __init__(self, job_info):
        self.jobid, self.user, self.status, self.queue, self.from_host = job_info[:5]
        self.submit_time = ' '.join(job_info[-3:])
        self.name = job_info[-4]
        if len(job_info) == 10:
            star_pos = job_info[5].find('*')
            if star_pos == -1:
                print("Wrong job info.")
                exit
            else:
                self.n_cpu = int(job_info[5][:star_pos])
        else:
            self.n_cpu = 0

    def brief(self):
        return "Job "+self.jobid+ " ("+self.name+") "

    def print_status(self):
        print(brief(self)+"is " + self.status + "ING.")
        return

    def print_n_cpu(self):
        print(brief(self)+"runs on "+self.n_cpu+" processors.")

class JobList:
    def __init__(self):
        self.job_list = []
        # some initialization here, in case that check_bjobs() hasn't been called
        self.n_job = 0
        self.n_cpu = 0
        self.header = []

    def update_joblist(self, temp_job_list):
        original_jobs_exist = np.zeros(len(self.job_list))
        now_jobs_new = np.zeros(len(temp_job_list))
        for count, item in enumerate(temp_job_list):
            new_job = 1
            for count2, item2 in enumerate(self.job_list):
                if item.jobid == item2.jobid:
                    original_jobs_exist[count2] = 1
                    new_job = 0
                    break;
            if new_job == 1:
                now_jobs_new[count] = 1
        c = np.where(original_jobs_exist == 0)[0]
        email_body = ""
        if len(c) != 0:
            email_body += "Job(s) done (or killed):\n"
            for count, item in enumerate(c):
                email_body += self.job_list[item].brief()+'\n'
            self.job_list = [item for item in self.job_list if self.job_list.index(item) not in c]
        c = np.where(now_jobs_new == 1)[0]
        if len(c) != 0:
            email_body += "Job(s) added:\n"
            for count2, item2 in enumerate(c):
                self.job_list.append(temp_job_list[item2])
                email_body += temp_job_list[item2].brief()+'\n'
        if email_body == "":
            return "NULL"
        else:
            return email_body

    def check_bjobs(self):
        temp_job_list = []
        self.n_cpu = 0
        self.n_job = 0
        bjobs = subprocess.check_output("bjobs", stderr=subprocess.STDOUT)
        if bjobs != "No unfinished job found\n":
            jobs = bjobs.split('\n')
            self.header = jobs[0].split()
            count = 1
            while count < len(jobs):
                if len(jobs[count]) == 0:
                    count += 1
                else:
                    if jobs[count][0] != ' ':
                        temp_job_list.append(Job(jobs[count].split()))
                        self.n_job += 1
                        if temp_job_list[-1].status == "RUN":
                            self.n_cpu += temp_job_list[-1].n_cpu
                    else:
                        star_pos = jobs[count].split()[0].find('*')
                        if star_pos == -1:
                            print("Wrong bjobs output.")
                            exit
                        temp_number = int(jobs[count].split()[0][:star_pos])
                        temp_job_list[-1].n_cpu += temp_number
                        self.n_cpu += temp_number
                count += 1
            print("n_cpu = ", self.n_cpu)
            return self.update_joblist(temp_job_list)
        else: # i.e. if bjobs == "No unfinished job found\n"
            return "None"

class Unsubmitted_JobList:
    def __init__(self, available_cpu):
        self.n_max_cpu = available_cpu
        self.unsufficient_cpu_flag = 0

    def f(self, v, i, S, memo):
        if i >= len(v): return 1 if S == 0 else 0
        if (i, S) not in memo:  # <-- Check if value has not been calculated.
            count = self.f(v, i + 1, S, memo)
            count += self.f(v, i + 1, S - v[i], memo)
            memo[(i, S)] = count  # <-- Memoize calculated result.
        return memo[(i, S)]     # <-- Return memoized value.

    def g(self, v, S, memo):
        subset = []
        for i, x in enumerate(v):
            # Check if there is still a solution if we include v[i]
            if self.f(v, i + 1, S - x, memo) > 0:
                subset.append(x)
                S -= x
        return subset

    def submit_job(self, lsf_path):
        slash_pos = lsf_path.rfind('/')
        dir_path = lsf_path[:slash_pos]
        lsf_name = lsf_path[slash_pos+1:]
        cmd = "/bin/bash /home/u5/rixin/bin/pysub_jobs "+dir_path+" "+lsf_name
        print("From submit_job(): "+cmd)
        bsub = subprocess.call(shlex.split(cmd), stderr=subprocess.STDOUT)
        return
    
    def check_given_file(self, filepath, n_cpu):
        with open(filepath) as unsubmitted_jobs_file:
            unsubmitted_jobs_path = unsubmitted_jobs_file.read().splitlines()
        jobs_path = [x for x in unsubmitted_jobs_path if len(x) != 0]
        submitted_jobs_path = [x for x in unsubmitted_jobs_path if x[0] == '#']
        unsubmitted_jobs_path = [x for x in unsubmitted_jobs_path if len(x) != 0 and x[0] != '#']
        
        if n_cpu <= 0:
            return len(unsubmitted_jobs_path)        
        if len(unsubmitted_jobs_path) != 0:
            cpu_need = []
            for count, item in enumerate(unsubmitted_jobs_path):
                cmd = 'grep -in "#BSUB\ -n" '+item
                cpu_need.append(int(subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT).split()[-1]))
            if self.n_max_cpu < max(cpu_need):
                print("WARNING: Some jobs need more processors than allocated!")
                self.unsufficient_cpu_flag = 1
            if n_cpu < min(cpu_need):
                return len(unsubmitted_jobs_path)
            else:
                for count in reversed(range(1, n_cpu+1)):
                    memo = dict()
                    if self.f(cpu_need, 0, count, memo) == 0:
                        continue
                    else:
                        cpu_list2submit = self.g(cpu_need, count, memo)
                        for count2, item2 in enumerate(cpu_list2submit):
                            temp_index = cpu_need.index(item2)
                            self.submit_job(unsubmitted_jobs_path[temp_index])
                            submitted_jobs_path.append('#'+unsubmitted_jobs_path[temp_index])
                            del cpu_need[temp_index], unsubmitted_jobs_path[temp_index]
                        all_jobs = '\n'.join(unsubmitted_jobs_path+submitted_jobs_path)
                        jobs_file = open(filepath, "w")
                        jobs_file.write(all_jobs+'\n')
                        jobs_file.close()
                        return len(unsubmitted_jobs_path)
        else: # i.e. if len(unsubmitted_jobs_path) == 0
            return 0

# main function, if you call this as main function
if __name__ == '__main__':

    # dealing with arguments
    import argparse
    parser = argparse.ArgumentParser(description="This is an script to submit and monitor multiple jobs.")
    parser.add_argument('-p', '--path', dest="path", help="Path of a file which contains lsf.sh files (default: /home/u5/rixin/runs/kkruns/jobs2run.txt)", default="/home/u5/rixin/runs/kkruns/jobs2run.txt")
    parser.add_argument('-n', '--ncpus', dest="ncpus", help="Maximum number of processors to use (default: 64)", type=int, default=64)
    parser.add_argument('-e', '--email', dest="email", help="If set, then job monitor will send email to report status", action='store_const', const=True, default=False)
    parser.add_argument('-c', '--comment', dest="comment", help="Subject post-comment for emails", default="default")
    args = parser.parse_args()

    JL = JobList()
    UJL = Unsubmitted_JobList(args.ncpus)
    
    bjobs = JL.check_bjobs()
    jobs_left = UJL.check_given_file(args.path, args.ncpus-JL.n_cpu)
    if UJL.unsufficient_cpu_flag == 1:
        print("Need more processors!")
        sys.exit(1)
    print("jobs_left = ", jobs_left)
    time.sleep(30)

    # main loop
    bjobs = JL.check_bjobs()
    if bjobs == "None" and jobs_left == 0:
        if args.email:
            send_to_myself("Nothing needs to be done!", "None")
        sys.exit(0)
    else:
        if args.email:
            send_to_myself("Job-Monitor launching "+args.comment+current_datetime_string(), bjobs)
        while bjobs != "None" or jobs_left != 0:
            jobs_left = UJL.check_given_file(args.path, args.ncpus-JL.n_cpu)
            time.sleep(30)
            bjobs = JL.check_bjobs()
            print "JL.n_cpu = ", JL.n_cpu
            if bjobs[0] != 'N':
                print("jobs_left = ", jobs_left)
                if args.email:
                    send_to_myself("Job-Monitor update "+args.comment+current_datetime_string(), bjobs)
        else:
            send_to_myself("Job-Monitor done "+args.comment+current_datetime_string(), "Good Luck with data analyses.")

    # done
        
    
    
