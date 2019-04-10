#! /usr/bin/env python3.7

from box_jira import Jira
from collections import OrderedDict as order
from termcolor import cprint,colored
import argparse
from ticket import Ticket
from package import Package
from config import Config
from reports import Report
from example import Example



#main method to rout program fellow
def main():
    #Argument parser for Jira
    parser=argparse.ArgumentParser()
    parser.add_argument('--ticket','-t',help='Accept ticket number and shows hostname and packages')
    parser.add_argument('--host',help='Accept hostname and show related tickets and packages')
    parser.add_argument('--filename','-f',help='Accept host file and shows related tickets to each host and Packages')
    parser.add_argument('--new','-n',help='Creat new config file')
    parser.add_argument('--config','-c',help='Accept config file, Run query show hosts and related tickets and packages')
    parser.add_argument('--query','-q',help='Query name in config file -c should be set')
    parser.add_argument('--verify',nargs='?',const='verify',help='Verifying the host in a tiocket and show status of hosts, it needs ticket number')
    parser.add_argument('--report',help='Create CSV file from a Jira query')
    parser.add_argument('--comment',help='post verify output as a comment into ticket ')
    parser.add_argument('--export','-e',help='Export verification output to a file , it needs a filename or default will be output.txt')
    parser.add_argument('--example',help='Show usage examples use --example example ')
    args=parser.parse_args()
    #conditional for arguments
    if args.export:
        export=args.export
    else:
        export=False
    if args.config and args.query and not args.report and not args.verify:
        tickets.tickets_hosts(args.config,args.query)
    elif args.report == 'patching':
        report.email_report()
    elif args.host:
        tickets.host(args.host)
        #host(args.host)
    elif args.ticket and not args.filename:
        tickets.ticket(args.ticket)
    elif args.ticket == 'check' and args.filename:
        tickets.ticket_files(args.filename)
    elif args.comment:
        package.post_comment(args.comment)
    elif args.verify != 'verify' and not args.config and not args.query:
        package.single_ticket(args.verify,export)
    elif args.filename:
        tickets.filename(args.filename)
    elif args.new:
        config.config_create(args.new)
    elif args.verify == 'verify'  and args.config and args.query:
        package.multiple_tickets(args.config,args.query)
    elif args.example :
        Example.example()
    else:
        jira_query="None has been set"
        print(colored("Wrong input! please use --help to learn more about program",'red'))
config=Config()
package=Package()
tickets=Ticket()
report=Report()
if __name__ == '__main__':
    main()
