#! /usr/bin/env python3.7

from box_jira import Jira
from collections import OrderedDict as order
from termcolor import cprint,colored
import argparse
from config import Config
import re




class Ticket:

    def __init__(self):
        self.jira=Jira()
        self.config=Config()



    def unknown_host(self,hostname):


        keys=[]
        jira_query =f'project = INFOSEC AND issuetype = "Infra Vuln" AND status in (Open, "In Progress", "In Review") AND Hostnames ~ {hostname}'
        issues=self.jira.get_issues(jira_query)
        for issue in issues:
            keys.append(issue.key)
        return keys



    def host(self,hostname):
        try:
            # jira_query ='issuetype = "Infra Vuln" AND status in (Open, "In Progress") AND Hostnames ~  '+hostname
            jira_query ='issuetype = "Infra Vuln" AND status in (Open, "In Progress") AND text ~  '+hostname
            issues=self.jira.get_issues(jira_query)
            print('\n')
            if issues.total == 0:
                color = 'red'
            else:
                color = 'cyan'
            print(colored(str(issues.total)+" ticket(s) found",color))
            print('****************************')
            print(colored('Tickets for hostname: ','green'),colored(hostname,'green'))
            print('****************************')
            if issues.total > 0:

                # hostc=0
                for issue in issues:
                    des={}
                    hosts_lines=[]
                    shouldbe=[]
                    should2=[]
                    packages=[]
                    p2=[]
                    print('-------------------------------')
                    print(colored('IssueKey: '+issue.key,'green'))
                    print(colored('https://jira.inside-box.net/browse/'+issue.key,'blue'))
                    pattern1=r"kernel-[\d]"
                    pattern2=r"kernel-[a-z]+"
                    description=issue.fields.description.split('\n')

                    for line in description:
                        if 'Should be' in line:
                            should2.append(line.split(':')[1].strip())
                    shouldbe=list(order.fromkeys(should2))
                    for line in shouldbe:
                        if re.match(pattern1,line):
                            p2.append('kernel')
                        elif re.match(pattern2,line):
                            p2.append(str(re.match(pattern2,line).group(0)))
                        else:
                            p2.append(line)
                    packages=list(order.fromkeys(p2))
                    for line in packages:
                        print(colored('> '+line,'yellow'))
        except:
            print(colored(f'Error! there is no ticket for {hostname}','red'))



#return list of the ticket for use in any other methods
    def host_finder(self,hostname):
        host=[]
        jira_query ='issuetype = "Infra Vuln" AND status in (Open, "In Progress") AND text ~  '+hostname
        try:
            issues=self.jira.get_issues(jira_query)
            if issues.total > 0:
                for issue in issues:
                    host.append(issue.key)
            return host
        except:
            host.append('N/A')
        





    def ticket(self,ticketno):
        try:
            jira_query ='issuekey ='+ticketno
            issues=self.jira.get_issues(jira_query)

            print('\n')
            print('****************************')
            print(colored('Ticket : ','green'),colored(ticketno,'green'))
            print('****************************')
            for issue in issues:
                hostnames=(issue.fields.customfield_12094.split(','))
            print(colored('List of hosts:','green'))
            hostnames.sort()
            for host in hostnames:
                print(host.split(':')[0])
        except:
            print(colored(f'Error! Issuekey: "{ticketno}" is not exsit!','red'))



#read config file and read jira query execute it and show hosts on each query
    def tickets_hosts(self,config,query):
        hostnames=[]
        hostname=[]

        jira_query=self.config.config_reader(config,query)
        issues=self.jira.get_issues(jira_query)
        print("Total Tickets: ",issues.total)
        print("Hostnames are :\n-----------------")
        for issue in issues:
            hostnames.append(issue.fields.customfield_12094.split(','))
        for hosts in hostnames:
            for host in hosts:
                hostname.append(host)
        hostname_unique=list(order.fromkeys(hostname))
        hostname_unique.sort()
        for host in hostname_unique:
            print(host.split(':')[0])
        print(f'--------------\nTotal Hosts:{len(hostname_unique)}')




#read host file and show related ticket for each host
    def filename(self,filename):
        with open(filename) as f:
            lines=f.readlines()

        for line in lines:
            hostname=line
            try:
                jira_query ='issuetype = "Infra Vuln" AND status in (Open, "In Progress") AND text ~  '+hostname
                issues=self.jira.get_issues(jira_query)
                print('\n')
                if issues.total == 0:
                    color = 'red'
                else:
                    color = 'cyan'
                print(colored(str(issues.total)+" ticket(s) found",color))
                print('****************************')
                print(colored('Tickets for hostname: ','green'),colored(hostname,'green'))
                print('****************************')
                if issues.total > 0:
                    for issue in issues:
                        des={}
                        hosts_lines=[]
                        shouldbe=[]
                        hostc=0
                        print(colored('IssueKey: '+issue.key,'green'))
                        print(colored('https://jira.inside-box.net/browse/'+issue.key,'blue'))

                        description=issue.fields.description.split('\n')
                        for line in description:
                            if hostname in line:
                                pass
                            elif 'Should' in line and hostc == 0 :
                                print(colored('Package '+line.split(':')[1].split('-')[0],'yellow'))
                                hostc += 1
                                print('------------------------------')
                            else:
                                continue
            except:
                print(colored(f'Error! there is no ticket for {hostname}','red'))


    def ticket_files(self,filename):
        tickets=[]
        with open(filename) as f:
            tickets=f.readlines()
        try:
            for ticket in tickets:
                jira_query ='issuekey ='+ticket
                issues=self.jira.get_issues(jira_query)

                for issue in issues:
                    hostnames=(issue.fields.customfield_12094.split(','))
                for host in hostnames:
                    print(host.split(':')[0])
        except:
            pass
