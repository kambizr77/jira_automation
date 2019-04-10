from subprocess import Popen,PIPE,run
import os
from ipchekcer import IpChecker



def main():
    ip=IpChecker()
    with open('list','r') as f:
        hosts=f.readlines()
    sshable=[]
    nosshable=[]
    ssh_dict={}
    no_ping=[]
    comm='uname -r'
    for host in hosts:
        hostname="root@"+host.strip()
        command=["sshpass","-p","1pm185h1t@B0xC@f3","ssh", "-o", "StrictHostKeyChecking=no","-o","BatchMode=yes",hostname,"show"]
        #command=["sshpass","-p","1pm185h1t@B0xC@f3","ssh",hostname,"show"]
        ssh=Popen(command,stdout=PIPE,stderr=PIPE)
        ssh_result=ssh.stdout.read().decode('utf-8')
        if len(ssh_result) > 0:
            ssh_dict.update({host.strip():ssh_result})
        else:
            nosshable.append(host.strip())

    with open('sshable.txt','w') as f:
        for key,value in ssh_dict.items():
            f.write(key+'\n')
    with open('nosshable.txt','w') as f:
        for item in nosshable:
            f.write(item+'\n')

    with open('nosshable.txt','r') as f:
        lines=f.readlines()
    host_dic={}
    for host in lines:
        command=['nmap',host.strip()]
        ports=Popen(command,stdout=PIPE,stderr=PIPE)
        temp=ports.communicate()[0].decode('utf-8')
        temp2=temp.split('\n')
        temp=[]
        for item in temp2:
            if 'tcp' in item and 'open' in item:
                temp.append(item.split('/')[0])
        host_dic.update({host:temp})
    with open('nosshable.txt','w') as f:
        for key,value in host_dic.items():
            f.write(key.strip('\n')+':'+str(value)+'\n')
