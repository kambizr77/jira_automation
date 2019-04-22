

import subprocess
import sys
import json
from box_jira import Jira
from termcolor import colored
from collections import OrderedDict as order
import progressbar
from config import Config
import re
from ticket import Tickets


class Verify:
    def   __init__(self,filename):
        self.filename = filename

    def issue_jira(self,jira_query):
        jira=Jira()
        issues=jira.get_issues(jira_query)
        return issues

    def hostnames(self):
        with open (self.filename , 'r') as f:
            hostnames=f.readlines()
        return hostnames

        #check host reachability
    def host_up(self,host):
        status,result=subprocess.getstatusoutput("ping -c 1 "+host.split(':')[0])
        if status == 0:
            return True
        else:
            return False

    def packages(self,issues,host):
        pkgs=[]
        packages=[]
        for issue in issues:
            description=issue.fields.description.split('\n')
            for line in description:
                bar_desc.update(i)
                if 'Remote' in line  :
                    pkgs.append(line.split(':')[1])
                else:
                    continue
            for pkg in pkgs:
                pkg2=re.search(pattern,pkg).group(0)
                    ssh_list = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                                            "-o", " BatchMode=yes", "%s" % host.split(':')[0],
                                            "sudo yum list  %s | grep %s" % (pkg, pkg2)],
                                           shell=False,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)

                    result1=ssh_list.stdout.read()
                    result2=result1.decode('utf-8')
                    package=result2.split(' ')[0]
                    if package not in packages:
                        if '.x86_64' in package:
                            packages.append(package.replace('.x86_64',''))
                        elif '.i686' in package:
                            packages.append(package.replace('.i686',''))
                        else:
                            packages.append(package)
        return packages

    def vrification(self,host,packages):
        update=[]
        noupdate=[]
        update_list_temp=[]
        for package in packages:
            ssh = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                        "-o", " BatchMode=yes", "%s" % host.split(':')[0],
                        "sudo yum check-update  %s | grep %s" % (package, package)],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
            result1=ssh.stdout.read()
            result2=result1.decode('utf-8')
            if len(result2) > 0:
                noupdate.append(host)
                update_list_temp.append(package)
            else:
                update.append(host)


        if len(noupdate) > 0:
            noupdate2=list(order.fromkeys(noupdate))
            update_list=list(order.fromkeys(update_list_temp))
        else:
            noupdate2=[]

        return noupdate2,update,update_list


    def host_list_verify(self):
        down=[]
        result={}
        packages=[]
        ticket=Ticket()
        hostnames=self.hostnames()
        for host in hostnames:
            if self.host_up(host):
                tickets=host_finder(host)
                for ticket in tickets:
                    jira_query ='issuekey ='+ticket
                    issues=issue_jira(jira_query)
                    packages.append(self.packages(issues,host))
                    noupdate2,update,update_list=verification(host,packages)
            else:
                down.append(host)
