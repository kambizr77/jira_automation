
#! /usr/bin/env python3.7
import configparser as ConfigParser
import os
from jira import JIRA
from termcolor import cprint,colored
import requests
from collections import OrderedDict as order
import argparse
import re
from pathlib import Path
import getpass
import subprocess as sp
class Jira:
    """Class to connect to Box's implementation of Jira

    This class pulls in the unsername/password from a config to connect to the
    API. It's functions pull information out of Jira.

    The class also pulls out vulnerability information from tickets.

    """

    def __init__(self):
        """Initialize the passwords, base_url, headers for the API"""


        config = ConfigParser.ConfigParser()
        package_directory = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(package_directory, '.jira.cnf'))
        user = config.get('jira', 'user')
        password = config.get('jira', 'password')
        #read main config file and auth with jira
        # home=str(Path.home())
        # self.config = ConfigParser.ConfigParser()
        # package_directory = os.path.dirname(os.path.abspath('jira.cnf'))
        # jira_file=home+'/.jira.cnf'
        # while not os.path.isfile(jira_file):
        #     print('Your Login config file has not be found!, Please create your own login config file')
        #     username=input("Please enter your username: ")
        #     password_jira=getpass.getpass(prompt='Please enter your password: ',stream=None)
        #     with open(jira_file,'w') as f:
        #         f.write('[jira]\n')
        #         f.write(f'user = {username}\n')
        #         f.write(f'password = {password_jira}')
        #     print(f'Config file generated sucessfully, To edit the file please edit: {jira_file}')

        # self.config.read(os.path.join(package_directory, 'jira.cnf'))
        # sp.call(['chmod','700',jira_file])
        # self.config.read(jira_file)
        # user = self.config.get('jira', 'user')
        # password = self.config.get('jira', 'password')
        auth = (user, password)
        options = {'server': 'https://jira.inside-box.net'}
        self.jira = JIRA(options, auth=auth)



    def get_issues(self,jira_query):
        """Genarte the output of Jira """


        issues=self.jira.search_issues(jira_query,maxResults=None)
        return issues








def main():
    pass


if __name__ == '__main__':
    main()
