#!/home/box_report/box/bin/python


from subprocess import Popen,PIPE,run
import os,json
from ipchecker import IpChecker
from excel import Excel
from ticket import Ticket
from datetime import datetime as dt
from box_email import BoxEmail
from collections import OrderedDict as order
from nomad import Nomad


def pdu_ip_range_finder():
    with open('dhcpd.conf') as f:

        lines = f.readlines()
    line_number=[]
    temp=[]
    i=0
    for line in lines:
        if 'adc_gen4_cdu' in line or 'adc_gen3_cdu' in line :
            line_number.append(i)

        i += 1
    ip_range=[]
    for num in line_number:
        if 'range' in lines[num-1]:
            ip_range_temp=lines[num-1].split()[1:]
            if len(ip_range_temp) > 1:
                oct1=ip_range_temp[0].split('.')[3]
                oct2=ip_range_temp[1].split('.')[3].replace(';','')
                result=int(oct2) - int(oct1)
                if result == 1:
                    ip_range.append(ip_range_temp[0])
                    ip_range.append(ip_range_temp[1].replace(';',''))
                elif result > 1:
                    n=0
                    while n <= result:

                        last_oct=int(oct1)+int(n)
                        octs=ip_range_temp[0].split('.')[:3]
                        ip_range.append(str(octs[0])+'.'+str(octs[1])+'.'+str(octs[2])+'.'+str(last_oct))
                        n += 1
    return ip_range

def oob_ip_range_finder():
    oob_ips=[]
    for oct3 in range(0,255):
        for oct4 in range(0,255):
            oob_ips.append('10.111.'+str(oct3)+'.'+str(oct4))
            oob_ips.append('10.47.'+str(oct3)+'.'+str(oct4))
            oob_ips.append('10.63.'+str(oct3)+'.'+str(oct4))
            oob_ips.append('10.238.'+str(oct3)+'.'+str(oct4))
            oob_ips.append('10.239.'+str(oct3)+'.'+str(oct4))
            oob_ips.append('10.240.'+str(oct3)+'.'+str(oct4))
            oob_ips.append('10.241.'+str(oct3)+'.'+str(oct4))

    return oob_ips

def owner_finder(hosts):
    ticket=Ticket()
    hosts_ticket={}
    with open('owner.json') as f:
        owners=json.load(f)
    for host in hosts:
        ticketno=ticket.unknown_host(host)
        hosts_ticket.update({host.strip('\n'):ticketno})
    return hosts_ticket,owners


def data_create():
    nomad=Nomad()
    ip_range=pdu_ip_range_finder()
    # cmd=os.system('./un.sh > all_unknown.txt')
    with open('manual_unknown.txt','r') as f:
        hosts=f.readlines()
    ip=IpChecker()
    bucket=ip.ip_check()
    oob_ips=oob_ip_range_finder()
    hosts_ticket,owners=owner_finder(hosts)
    data={}
    emails=[]
    for key,value in hosts_ticket.items():
        nomad_data=nomad.check_host(key)
        for keys,values in bucket.items():
            i=len(values)
            if i > 0:
                j=0
                temp_ip=[]
                while i > j:
                    temp_ip.append(str(values[j]))
                    j += 1
                for ip in temp_ip:
                    if key in ip and key not in ip_range and key not in oob_ips:
                        owner_key=keys.split('_')[0]
                        owner_name=owners[owner_key][keys]['owner']
                        if owners[owner_key][keys]['email'] != 'NA' and owners[owner_key][keys]['email'] not in emails:
                            emails.append(owners[owner_key][keys]['email'])
                        data.update({key:[keys,str(owner_name),value,nomad_data]})
                    elif key in ip_range:
                        owner_name='Clay Alvord'
                        emails.append('calvord@box.com')
                        data.update({key:['PDU-OOB',str(owner_name),value,nomad_data]})
                    elif key in oob_ips:
                        owner_name='Clay Alvord'
                        emails.append('calvord@box.com')
                        data.update({key:['OOB',str(owner_name),value,nomad_data]})
    return data,emails

def main():
    data,emails=data_create()
    email=list(order.fromkeys(emails))
    filename='unknow.xlsx'
    worksheet='unknown'
    headings=['IP','Base Type','Name','Tickets','Nomad Data','Ping-able','Inband FQDN','PROVISIONING_NEW_HOSTNAME']
    result=Excel.excel_writer(filename,worksheet,headings,data)

    if result:
        #email's body
        mydate = dt.now()
        date_string = dt.now().strftime("%Y-%m-%d")
        html=f'''<html>
        <head>
            <h1 style="color:red;">Unknown IPs weekly Report</h1>
            <h3 style="color:blue;">Report date: {date_string}</h3>
            <hr>
            <br>

        </head>
            <body>
            <p>
                If you are receiving this email, we've identified unknown IPs which we believe your team owns. We request you take the following action, to help validate whether the IPs belong to one of your services.
            </p>
            <ul>
                    <li> Open the attached spreadsheet, and filter by your name</li>
                    <li> Confirm the IP belongs to your team</li>
                    <li> Request DNS entries for these IPs</li>
            </ul>
            <p>
                Once you've created the DNS entry, during the next vulnerability scan,
                a ticket will be generated within your team's backlog base on service ownership details in Service Cat.
            </p>
            <p>
                If you do no believe the IPs belong to one of your services,
                please drop into the <a href='https://box.slack.com/app_redirect?channel=vts'>#vts</a> Slack channel, or reach out directly to our team at infrasec@box.com.
            </p>

        <p>Thank You</p>
        <hr>
        <br>
<p><small><mark><u>This is an automatic email</u></mark></small></p>
            </body>
        '''

        recipients1 = ['kevinf@box.com','plandry@box.com','mkim@box.com','nmilman@box.com','sdeol@box.com','anum@box.com','sfong@box.com'] + email

        recipients = recipients1
        #toaddr=recipients
        toaddr=['kambizrahmani@box.com']
        fromaddr='kambizrahmani@box.com'
        subject=f'Unknow IPs {date_string}'
        email = BoxEmail(toaddr, fromaddr, subject,filename)
        email.send_email(html)
        print(f"Script has been excutes at {date_string}")
if __name__ == '__main__':
    main()
