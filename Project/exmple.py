
from termcolor import colored

class Example:
    def example():
        print(colored('Examples:','cyan'))
        print('-'*10)
        print('''Find related tickets to the a host:
        main.py --host hostname.box.net
------------

export hostnames from a ticket:
        main.py --ticket BCK-1234
------------

Verifying a ticket:
        main.py --verify BCK-123
------------

Verify a ticket and export hostnames to a file:
        main.py --verify BCK-123 --export file.txt
------------

Find tickets for several hostnames stored in a file
        main.py --filename file.txt
------------

Export hostnames from several tickets which issue_key stored in a filename
        main.py --ticket check --filename file.txt
------------

Create a config file:
config file is for to store your jira queries and use it for latter user
        main.py --new config_file_name.cnf
------------

Use config file to export hostnames:
        main.py --config config_name.cnf --query query_name
------------

Use Config File to verify multiple tickets: It generate several text file and export hostnames of each ticket to diffrent tetxt filename
        main.py --config config.cnf --query query_name --verify
------------

        ''')
