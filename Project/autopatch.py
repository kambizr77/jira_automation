#! /usr/bin/env python3.7

import subprocess
import sys
import time
import json
from termcolor import colored
from collections import OrderedDict as order
import progressbar
from config import Config
import re
from box_jira import Jira
from ticket import Ticket

class Autopatch():
    def __init__(self,file_name):
        self.file_name = file_name
        self.ticket = Ticket()
        with open (self.file_name, 'r') as f:
            self.hostnames=f.readlines()

#return issue in Jira
    def issue_jira(self,jira_query):
        jira=Jira()
        issues=jira.get_issues(jira_query)
        return issues

#ping the host and return status
    def host_up(self,host):
        status,result=subprocess.getstatusoutput("ping -c 1 "+host)
        if status == 0:
            return True
        else:
            return False

#Ticket reader
    def ticket_reader(self,issue_keys):
        pkgs=[]
        for key in issue_keys:
            jira_query =f'issuekey = {key} and status not in(Completed)'
            issues_package=self.issue_jira(jira_query)
            for issue in issues_package:
                description=issue.fields.description.split('\n')
                for line in description:
                    if 'Remote' in line  :
                        pkgs.append(line.split(':')[1])
                    else:
                        continue
        return pkgs

#host package check
    def host_pkg_ckeck(self,host,pkgs):
        packages=[]
        pattern=re.compile(r'([\w]+)')
        for pkg in pkgs:
            pkg2=re.search(pattern,pkg).group(0)
            ssh_list = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                                    "-o", " BatchMode=yes", "%s" % host,
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

#check server Status
    def check_status(self,host):
        ssh_list = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                                "-o", " BatchMode=yes", "%s" % host,
                                "sudo server-enabled status | grep Status"],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result1=ssh_list.stdout.read()
        result2=result1.decode('utf-8')
        if 'enabled' in result2:
            return True
        else:
            return False

#enable host
    def do_enable(self,host):
        disable = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                                "-o", " BatchMode=yes", "%s" % host,
                                "sudo server-enabled enable --unlock --comment 'Enabled After patching' | grep Status"],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        res=disable.stdout.read()
        result=res.decode('utf-8')
        if 'enable' in result:
            return True
        else:
            return False

#Disable host
    def do_disable(self,host):
        disable = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                                "-o", " BatchMode=yes", "%s" % host,
                                "sudo server-enabled disable --lock --comment 'Disabled for patching' | grep Status"],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        res=disable.stdout.read()
        result=res.decode('utf-8')
        if 'disable' in result:
            return True
        else:
            return False

# Create a list of hosts with data
    def host_data(self):
        hosts={}
        for host in self.hostnames:
            issue_keys=self.ticket.host_finder(host.strip())
            status=self.host_up(host.strip())
            if issue_keys:
                pkgs=self.ticket_reader(issue_keys)
                if status:
                    packages=self.host_pkg_ckeck(host.strip(),pkgs)
                    enable=self.check_status(host.strip())
                    hosts.update({host.strip():{'issue':issue_keys,'status':status,'pkgs':packages,'enabled':enable}})
                else:
                    hosts.update({host.strip():{'issue':issue_keys,'status':False,'pkgs':None,'enabled':False}})
            else:
                if status:
                    hosts.update({host.strip():{'issue':None,'status':status,'pkgs':None,'enabled':False}})
                else:
                    hosts.update({host.strip():{'issue':None,'status':False,'pkgs':None,'enabled':False}})
        return hosts
# ###########Package update section
    def yum_clean(self,host):
        print("yum clean")
        kernel_cleaner = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                                "-o", " BatchMode=yes", "%s" % host,
                                "sudo yum clean all"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result1=kernel_cleaner.stdout.read()
        result2=result1.decode('utf-8')
        print(result2)

    def kernel_update(self,host):
        print("kernel_cleaner")
        kernel_cleaner = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                                "-o", " BatchMode=yes", "%s" % host,
                                "sudo /box/bin/kernel_cleaner"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result1=kernel_cleaner.stdout.read()
        result2=result1.decode('utf-8')
        print(result2)
        self.yum_clean(host)
        kernel_install = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                                "-o", " BatchMode=yes", "%s" % host,
                                "sudo yum install","kernel","kernel-headers", "-y"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        result1=kernel_install.stdout.read()
        result2=result1.decode('utf-8')
        print(result2)
        kernel_update_package = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                                "-o", " BatchMode=yes", "%s" % host,
                                "sudo yum update" ,"perf" ,"python-perf" ,"microcode_ctl ","kernel-devel","-y"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result1=kernel_update_package.stdout.read()
        result2=result1.decode('utf-8')
        print(result2)
#
#
#
#
    def package_update(self,host,pkgs):
        for pkg in pkgs:

            package_update = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                                "-o", " BatchMode=yes", "%s" % host,
                                "sudo yum update -y","%s" % pkg],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
            result1=package_update.stdout.read()
            result2=result1.decode('utf-8')
            print(result2)
    def reboot(self,host):
        reboot = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no",
                            "-o", " BatchMode=yes", "%s" % host,
                            "sudo reboot now"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        result1=package_update.stdout.read()
        result2=result1.decode('utf-8')
        print(result2)
###########End od section

#Patching Method
    def patch(self):
        down=[]
        disabled_hosts=[]
        data=self.host_data()
        for key in data.keys():
            if data[key]['status']:
                while data[key]['enabled']:
                    if self.do_disable(key):
                        data[key]['enabled']=False
                        disabled_hosts.append(key)
                if len(data[key]['pkgs']) >= 1 :
                    if 'kernel' in data[key]['pkgs']:
                        data[key]['pkgs'].remove('kernel')
                        data[key]['pkgs'].remove('kernel-headers')
                        data[key]['pkgs'].remove('kernel-firmware.noarch')
                        if 'perf.x86_64' in data[key]['pkgs']: data[key]['pkgs'].remove('perf')
                        if 'python-perf.x86_64' in data[key]['pkgs']: data[key]['pkgs'].remove('python-perf')
                        if 'kernel-devel.x86_64' in data[key]['pkgs']: data[key]['pkgs'].remove('kernel-devel')
                        if 'microcode_ctl.x86_64' in data[key]['pkgs']: data[key]['pkgs'].remove('microcode_ctl')
                        self.kernel_update(key)
                        if len(data[key]['pkgs']) >= 1:
                            self.package_update(key,data[key]['pkgs'])
                    # else:
                    #     self.package_update(key,data[key]['pkgs'])


            # else:
            #     down.append(key)




def main():
    a=Autopatch('hosts')
    a.patch()


main()
