from box_jira import Jira
import csv
from datetime import datetime as dt
from config import Config
from box_email import BoxEmail
from collections import OrderedDict as order
from termcolor import colored
from excel import Excel
class Report:

    def __init__(self):
        self.config=Config()
        self.jira=Jira()
        self.excel=Excel()


    def email_report(self):

        mydate = dt.now()
        # patching vs service owner
        jira_query_total = self.config.config_reader('report.cnf','total')
        total_issues = self.jira.get_issues(jira_query_total)
        jira_query_patching = self.config.config_reader('report.cnf','patching')
        patching_total_issues = self.jira.get_issues(jira_query_patching)
        percentage=format((patching_total_issues.total*100)/total_issues.total,'.1f')
        # Critical and blockers issue within SLA

        jira_query_total_CB = self.config.config_reader('report.cnf','total_c_b')
        total_issues_CB = self.jira.get_issues(jira_query_total)
        jira_query_CB_sla = self.config.config_reader('report.cnf','total_c_b_sla')
        total_issues_CP_sla = self.jira.get_issues(jira_query_CB_sla)
        jira_query_CB_sla_no = self.config.config_reader('report.cnf','total_c_b_nosla')
        total_issues_CP_sla_no = self.jira.get_issues(jira_query_CB_sla_no)
        percentage_CB=format((total_issues_CP_sla.total*100)/total_issues_CB.total,'.1f')


        #demand sign report
        # summary=[]
        # package=[]
        # pkg=[]
        # nopkg=[]
        # demand=[]
        temp1=[]

        projects={}

        for issue in patching_total_issues:
            temp1.append(issue.fields.project.name)
        project_list=list(order.fromkeys(temp1))
        for name in project_list:
            projects.update({name:temp1.count(name)})

        # for issue in patching_total_issues:
        #     if ':' in issue.fields.summary:
        #         summary.append(issue.fields.summary)
        #     else:
        #         nopkg.append(issue.fields.summary)
        # for item in summary:
        #     package.append(item.split(':')[1].split(' ')[1].split(' ')[0])
        # for item in package:
        #     pkg.append(item+':'+str(package.count(item)))

        #Patching team report data
        # final_package=list(order.fromkeys(pkg))
        # for item in final_package:
        #     temp1.append(item.split(':')[0])
        #     temp2.append(int(item.split(':')[1]))
        # demand=[temp1,temp2]
        patching=[['Service Owner or APF','Patching Team'],[(total_issues.total-patching_total_issues.total),patching_total_issues.total]]
        # Blocker & crtical report data
        cb=[['Within SLA','Not in SLA'],[total_issues_CP_sla.total,total_issues_CP_sla_no.total]]

        self.excel.create_report(patching,cb,projects,patching_total_issues.total)

#email's body
        date_string = dt.now().strftime("%Y-%m-%d")
        html=f'''<html>
        <head>
            <h1 style="color:DodgerBlue;">Report for  {mydate.strftime("%B")}</h1>
            <hr>
            <br>
        </head>
            <body bgcolor='#fff5e6'>
                <h2>Automatic Patching Team reports</h2>
                <h3>Please find attached Excel sheet file</h3>

            </body>
        '''
        #
        toaddr=['kambizrahmani@box.com',]
        fromaddr='kambizrahmani@box.com'
        subject=f'Patching report {date_string}'
        email = BoxEmail(toaddr, fromaddr, subject,'./report.xlsx')
        # #
        email.send_email(html)

    # def csv_report(slef,name)
    #
    #     s
    #     csv_data={}
    #     date=dt.now()
    #     tstamp=date.strftime('%Y-%m-%d %H:%M')
    #     issues=self.jira.get_issues(jira_query)
    #     with open('new.csv',mode='w') as f:
    #         total=issues.total
    #         writer=csv.writer(f,dialect='excel')
    #         writer.writerow(["Total Issue is: ",total,'','','Report Generated at:',tstamp])
    #         writer.writerow(['Issue Key','Type','ID','Summary','Priority','Status',
    #                             'Created','SLA Time Remaining','Labels','Hostnames'
    #                         ])
    #         for issue in issues:
    #             csv_data.update({
    #                             issue.key:[issue.fields.issuetype.name,issue.id,
    #                             issue.fields.summary,issue.fields.priority,issue.fields.status,
    #                             issue.fields.created ,issue.fields.customfield_14290,
    #                             issue.fields.labels,issue.fields.customfield_12094
    #
    #                                 ]
    #                             })
    #
    #         for key,value in csv_data.items():
    #
    #             rows=[key,]
    #             for item in value:
    #                 rows.append(item)
    #             writer.writerow(rows)
