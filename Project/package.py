#! /usr/bin/env python3.7
"""Check packages

This module gets all the hosts from a Jira ticket then logs in and checks
for the installed packages.

"""

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

class Package:
    #connect to Jira REST and return ticket
    def issue_jira(self,jira_query):
        jira=Jira()
        issues=jira.get_issues(jira_query)
        return issues
    #it read a ticket and return hostnames and packages mentioned in a ticket
    def package_check(self,issues):
        pattern=re.compile(r'([\w_]+)')
        for issue in issues:
            # print(dir(issue.fields))
            print("Package: ",colored(issue.fields.summary.split(':')[1].split(' ')[1],'cyan'))
            hostnames=(issue.fields.customfield_12094.split(','))
            description=issue.fields.description.split('\n')
        bar0 = progressbar.ProgressBar(maxval=len(hostnames),widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar_desc = progressbar.ProgressBar(maxval=len(description),widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        print("Total Number of Hosts:",colored(len(hostnames),'red'))
        packages=[]
        h=0
        down=[]
        pkgs=[]
        print(colored("Reading ticket data ....",'cyan'))
        bar_desc.start()
        i=0
        for line in description:
            bar_desc.update(i)
            if 'Remote' in line  :
                pkgs.append(line.split(':')[1])
            else:
                continue
            i += 1

        bar_desc.finish()
        i=0
        print(colored("Package verification....",'cyan'))
        bar0.start()
        for host in hostnames:
            bar0.update(i)
            status=self.host_up(host)
            if h < 1:
                for pkg in pkgs:
                    pkg2=re.search(pattern,pkg).group(0)
                    if status:
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
                        h += 1
            if  not status:
                down.append(host)
            i += 1
            # h += 1
        bar0.finish()

        packages2=list(order.fromkeys(packages))
        return hostnames,packages2,down
    #check host reachability
    def host_up(self,host):
        status,result=subprocess.getstatusoutput("ping -c 1 "+host.split(':')[0])
        if status == 0:
            return True
        else:
            return False

#verify each host is patched or not
    def get_ticket_package(self,ticket_no):
        print(colored(f"Tikcet: {ticket_no}",'green'))
        update=[]
        noupdate=[]
        update_list_temp=[]
        jira_query ='issuekey ='+ticket_no
        issues=self.issue_jira(jira_query)
        hostnames,packages2,down=self.package_check(issues)
        print(colored("Hosts verification....",'cyan'))
        bar = progressbar.ProgressBar(maxval=len(hostnames),widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        i=0
        for host in hostnames:
            bar.update(i)
            if host not in down:
                for package in packages2:
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

            i += 1
        bar.finish()
        if len(noupdate) > 0:
            noupdate2=list(order.fromkeys(noupdate))
            update_list=list(order.fromkeys(update_list_temp))
        else:
            noupdate2=[]

        return noupdate2,down,update,packages2,update_list


#Writing output on afile
    def export_writer(self,noupdate2,down,packages2,export):
        file='./output/'+export
        if len(noupdate2) > 0 and len(down) > 0:
            noupdate2.sort()
            down.sort()
            with open(file,'w') as f:
                f.write('\nThe following hosts are not reachable\n')
                f.write('-------------------------------------\n')
                for host in down:
                    f.write(host.split(':')[0]+'\n')
                f.write('\n\n*************************************\n\n')
                f.write('The following hosts need update\n')
                f.write('-------------------------------------\n')
                for host in noupdate2:
                    f.write(host.split(':')[0]+'\n')

        elif len(noupdate2) == 0 and len(down) > 0:
            down.sort()
            with open(file,'w') as f:
                f.write('The following hosts are not reachable\n')
                f.write('-------------------------------------\n')
                for host in down:
                    f.write(host.split(':')[0]+'\n')

        elif len(noupdate2) > 0 and len(down) == 0:
            noupdate2.sort()
            with open(file,'w') as f:
                f.write('The following hosts need update\n')
                f.write('-------------------------------------\n')
                for host in noupdate2:
                    f.write(host.split(':')[0]+'\n')
        elif len(noupdate2) == 0 and len(down) == 0:
            with open(file,'w') as f:
                f.write('You do not have any hosts to patch and your ticket is ready for security review\n')
                f.write('-------------------------------------')


#main method for single ticket which execute by --verify
    def single_ticket(self,ticket,export=False):
        noupdate2,down,update,packages2,update_list=self.get_ticket_package(ticket)
        if export == False:
            if len(noupdate2) > 0 and len(down) > 0:
                print('-------------------------------------------------------')
                print(colored(f'You have {len(noupdate2)} hosts should be patch'))
                for item in packages2:
                    print(item)
                print(colored(f'You have {len(down)} hosts not reachable ','red'))
                for i in down:
                    print(colored('--------->','red'),i.split(':')[0])
                print(colored("Do you want the list of  hosts:(y/n)",'yellow'))
                while True:
                    answer=input('>')
                    if answer.lower() == 'y':
                        noupdate2.sort()
                        for item in noupdate2:
                            print(item.split(':')[0])
                        print('----Packages----')
                        for item in update_list:
                            print(item)
                        sys.exit()
                    elif answer.lower() == 'n':
                        sys.exit()
                    else:
                        print("Wrong input!")
            elif len(noupdate2) == 0 and len(down) > 0:
                print('-------------------------------------------------------')
                print(colored(f'You have {len(down)} hosts not reachable ','red'))
                for i in down:
                    print(colored('--------->','red'),i.split(':')[0])
                print('-------------------------------------------------------')
                print("All other hosts are updated")

            elif len(noupdate2) > 0 and len(down) == 0:
                print('-------------------------------------------------------')
                print(colored(f'You have {len(noupdate2)} hosts should be patch'))
                print(colored("Do you want the list of hosts:(y/n)",'yellow'))
                while True:
                    answer=input('>')
                    if answer.lower() == 'y':
                        noupdate2.sort()
                        for item in noupdate2:
                            print(item.split(':')[0])
                            print(update_list)
                        sys.exit()
                    elif answer.lower() == 'n':
                        sys.exit()
                    else:
                        print("Wrong input!")
            elif len(noupdate2) == 0 and len(down) == 0:
                print('-------------------------------------------------------')
                print(colored('You do not have any hosts to patch and your ticket is ready for security review','green'))
        else:
            print(export)
            self.export_writer(noupdate2,down,packages2,export)
            print(f"Output has been writen in ./output/{export}")

#Reading config file and use Jquery to fid tickets and verify each of the and write the output on each seprate file with issue_key.txt
    def multiple_tickets(self,configfile,query):

        config=Config()
        jira_query=config.config_reader(configfile,query)
        issues=self.issue_jira(jira_query)
        print(f'Verifying {colored(issues.total,"red")} Tickets... ')
        i=1
        for issue in issues:
            print(colored(f'No: {i} ','yellow'))
            file='./output/'+str(issue.key)+'.txt'
            noupdate2,down,update,packages2=self.get_ticket_package(issue.key)
            if len(noupdate2) > 0 and len(down) > 0:
                noupdate2.sort()
                down.sort()
                with open(file,'w') as f:
                    f.write('\nThe following hosts are not reachable\n')
                    f.write('-------------------------------------\n')
                    for host in down:
                        f.write(host.split(':')[0]+'\n')
                    f.write('\n\n*************************************\n\n')
                    f.write('The following hosts need update\n')
                    f.write('-------------------------------------\n')
                    for host in noupdate2:
                        f.write(host.split(':')[0]+'\n')

            elif len(noupdate2) == 0 and len(down) > 0:
                down.sort()
                with open(file,'w') as f:
                    f.write('The following hosts are not reachable\n')
                    f.write('-------------------------------------\n')
                    for host in down:
                        f.write(host.split(':')[0]+'\n')

            elif len(noupdate2) > 0 and len(down) == 0:
                noupdate2.sort()
                with open(file,'w') as f:
                    f.write('The following hosts need update\n')
                    f.write('-------------------------------------\n')
                    for host in noupdate2:
                        f.write(host.split(':')[0]+'\n')
            elif len(noupdate2) == 0 and len(down) == 0:
                with open(file,'w') as f:
                    f.write('You do not have any hosts to patch and your ticket is ready for security review\n')
                    f.write('-------------------------------------')

            i += 1









#
# def main():
#     pass
#
#
# if __name__ == '__main__':
#     main()
