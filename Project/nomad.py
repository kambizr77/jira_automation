import requests
import configparser as ConfigParser
import os
import urllib3
import subprocess as sp
from pathlib import Path
import getpass
class Nomad:
    def __init__(self):
        config = ConfigParser.ConfigParser()
        # package_directory = os.path.dirname(os.path.abspath(__file__))
        home=str(Path.home())
        nomad_file=home+'/.nomad.cnf'
        # config.read(os.path.join(package_directory, 'jira.cnf'))
        while not os.path.isfile(nomad_file):
            print('Your Login config file has not be found!, Please create your own login config file')
            username=input("Please enter your LDAP username: ")
            password_nomad=getpass.getpass(prompt='Please enter your LDAP password: ',stream=None)
            with open(nomad_file,'w') as f:
                f.write('[nomad]\n')
                f.write(f'user = {username}\n')
                f.write(f'password = {password_nomad}')
            print(f'Config file generated sucessfully, To edit the file please edit: {nomad_file}')
        sp.call(['chmod','700',nomad_file])
        config.read(nomad_file)
        user = config.get('nomad', 'user')
        password = config.get('nomad', 'password')
        self.auth = (user, password)

        session = requests.Session()
        session.verify = False


    def check_host(self,host):
        new_hostname='N/A'
        urllib3.disable_warnings()
        headers={'Content-type':'application/json'}
        base_url=f'https://nomad.prod.box.net/devicemgr/api/devices/?mgmt_ip={host}'
        rest=requests.get(url=base_url,auth=self.auth,headers=headers,verify=False)
        data=rest.json()
        # ping=Popen(['ping','-c 1',host],stdout=PIPE,stderr=PIPE)
        status,result=sp.getstatusoutput("ping -c 1 "+host)
        if status == 0:
            reach="Yes"
        else:
            reach="No"
        if data['count'] > 0:
            # 'PROVISIONING_NEW_HOSTNAME'
            for item in data['results'][0]['sparse']:
                if item['attribute']['name']=='PROVISIONING_NEW_HOSTNAME':
                    new_hostname=item['value']
            # if data['results'][0]['logentry_set'][0]['action'] == 'create':
            #     timestamp1=data['results'][0]['logentry_set'][0]['timestamp'].split('.')[0]
            #     timestamp=timestamp1.replace('T',' ')
            #     action='Create'
            # else:
            #     timestamp='N/A'
            #     action='N/A'
            # nomad_data={'Nomad':'Yes','fqdn':data['results'][0]['fqdn'],'action':action,'timestamp':timestamp}
            nomad_data={'Nomad':'Yes','reach':reach,'fqdn':data['results'][0]['fqdn'],'new_hostname':new_hostname}

        else:
            # nomad_data={'Nomad':'No','fqdn':'N/A','timestamp':'N/A','action':'N/A'}
            nomad_data={'Nomad':'No','reach':reach,'fqdn':'N/A','new_hostname':'N/A'}
        return nomad_data


def main():
    # a=Nomad()
    # req=a.check_host('10.111.128.113')
    # print(req)
    pass

if __name__ == '__main__':
    main()







#
# curl --insecure  'https://nomad-staging.dev.box.net/cmdb/api/sites/' \
# -H 'authorization: kambizrahmani Touraj@1325rahmani' \
# -H 'content-type: application/json' | jq
