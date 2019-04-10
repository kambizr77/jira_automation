

import sys
import netaddr
import argparse
from bitdoodle import BitDoodle
from pprint import pprint
from prettytable import PrettyTable

class BoxNetworkIp(netaddr.IPAddress):
    def __init__(self, addr, version=None, flags=0):
        super(BoxNetworkIp, self).__init__(addr, version, flags)
        self.mybits = self.bits(word_sep='')
        self.set_site()
        self.set_pod()

    def set_site(self):
        sites = {
            '0000': 'g2',
            '0001': 'g2',
            '0010': 'csv2',
            '0011': 'vsv1',
            '0100': 'esv2',
            '0101': 'publiccloud',
            '0110': 'slv8',
            '1110': 'dsv31',
            '1111': 'small_sites/edc',
        }
        self.site = sites.get(self.mybits[8:12], self.mybits[8:12])

    def set_pod(self):
        pods = {
            '00000': 'infrastructure',
            '11111': 'oob31',
            '11110': 'oob30',
        }
        if self.site != 'small_sites/edc' and self.site != 'g2':
            self.pod = pods.get(self.mybits[12:17], 'compute')
        else:
            self.pod = 'unknown'
