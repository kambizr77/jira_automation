#! /usr/bin/env python3.7
import configparser as ConfigParser
import os,sys
from box_jira import Jira


class Config:

    def __init__(self):

        self.config = ConfigParser.ConfigParser()

    def config_reader(self,configfile,queryname):
                package_directory = os.path.dirname(os.path.abspath(configfile))
                self.config.read(os.path.join(package_directory, configfile))
                jira_query = self.config.get('query',queryname )
                return jira_query


#create configfile and show it
    def config_create(self,name):
        configfile = name
        exists=os.path.isfile(configfile)
        if not exists:
            query_name=input("Please enter your Jira query name > ")
            query=input("Please enter your Jira query > ")
            with open(configfile,'w') as f:
                f.write('[query]\n')
                f.write(query_name+' = '+query)
            answer=input("Do you want to view configfile?(y/n) >")
            while True:
                if answer.lower() == 'y':
                    with open(configfile,'r') as f:
                        lines=f.readlines()
                    for line in lines:
                        print(line)
                    sys.exit()
                elif answer.lower() == n:
                    sys.exit()
                else:
                    print("Wrong input!")
        else:
            print(f"'{name}' is exist")
