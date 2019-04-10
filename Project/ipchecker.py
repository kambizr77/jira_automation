from boxnetworkip import BoxNetworkIp
from bitdoodle import BitDoodle
import netaddr



class IpChecker:

    def flatten(d, parent_key='', sep='_'):
        """Given a dictionary d, flatten it int a single dict of k: v.  Any child dict found just flattens the
        main dictionary key with key<sep>childkey<sep>nextchildkey etc.
        :param d: nested dictionary
        :param parent_key: string if you want to prepend everything
        :param sep: seperator
        :return: dict
        """
        items = []
        for k, v in d.items():
           new_key = parent_key + sep + k if parent_key else k
           if isinstance(v, dict):
               items.extend(IpChecker.flatten(v, new_key, sep=sep).items())
           else:
               items.append((new_key, v))
        return dict(items)

    def slurp_unknown_ips():
        """Slurp IP List File
        :return: a list of IP's
        """
        with open('all_unknown.txt') as f:
           content = f.readlines()
        ip_list = [x.strip() for x in content]
        return ip_list


    def ip_check(self):
        ips = list(set([BoxNetworkIp(ip) for ip in IpChecker.slurp_unknown_ips()]))
        ips = sorted(ips, key=lambda x: x.site, reverse=True)
        # this 'bucket' dict is basically where I put one of the IP's.  It must fit in one of the buckets.
        bucket = {
            'unknown': [],
            'g2': {
                'compute': {
                    'frontend': [],
                    'realtime': [],
                    'new_eng_access': [],
                    'storage_servers': [],
                    'internal_api': [],
                    'legacy_util': [],
                    'management': [],
                    'physical_infra_drac_pdu': [],
                    'database_servers': [],
                    'convert_servers': [],
                    'app_util_servers': [],
                    'app_backend_servers': [],
                    'iks_servers': [],
                    'dwh_cluster_hadoop': [],
                    'dmz_not_tagged': [],
                    'kickstart': [],
                    'traffic_manager': [],
                    'web_proxy': [],
                    'ftp_frontends': [],
                    'bastion': [],
                    'unknown': [],
                },
                'aws_data_platform': {
                    'dev': [],
                    'staging': [],
                }
            },
            'g3': {
                'unknown': [],
                'network_infra': [],
                'oob': {
                    'network_infra': [],
                    'dracs': [],
                    'pdu': [],
                },
                'compute': {
                    'network_infrastructure': [],
                    'boxfiler_and_storage': [],
                    'alf_servers': [],
                    'convert_servers': [],
                    'misc_backend_services': [],
                    'data_warehouse': [],
                    'database': [],
                    'management_and_infra': [],
                    'vmh_servers': [],
                    'pingsso': [],
                    'iks_keds_backend_security': [],
                    'notes_frontend': [],
                    'realtime': [],
                    'newsroom': [],
                    'skynet_container_services': [],
                    'adc_ipvs': [],
                    'trust_anchor': [],
                    'openstack_private': [],
                    'bastion': [],
                    'calico': [],
                    'infoblox': [],
                    'webproxy_and_jumphost': [],
                    'unknown': [],
                    'convert': [],
                    'frontend': [],
                    'dmz': [],
                    'skynet_container': [],
                    'internal_api': [],
                    'cab_local_shit': [],
                    'kickstart': [],
                    'tsw_vlan_ip': [],
                }
            },
            'g4': [],
            'edc': {
                'unknown': [],
                'network_infra': [],
                'oob': {
                    'network_infra': [],
                    'dracs': [],
                    'pdu': [],
                    'unknown': [],
                },
                'compute': {
                    'network_infra': [],
                    'ipvs-load-balancers-for-public-product': [],
                    'ipvs-load-balancers-for-vip-product': [],
                    'external-egress-nat-service': [],
                    'gen-ftp-servers': [],
                    'gen-ftp-servers-for-vip': [],
                    'gen-oob-bastion-and-utility-hypervisor': [],
                    'management-and-infrastructure': [],
                    'cabinet-local-network': [],
                    'server-hotcache': [],
                    'kickstart-network': [],
                    'unknown': [],
                },
            },
        }

        # See: https://confluence.inside-box.net/display/ETO/Subnet+and+VLAN+List#SubnetandVLANList-GlobalVLANs
        g2_vlan_list = {
            '16': 'frontend',
            '17': 'frontend',
            '18': 'frontend',
            '19': 'frontend',
            '20': 'frontend',
            '21': 'frontend',
            '22': 'frontend',
            '23': 'frontend',
            '24': 'frontend',
            '26': 'realtime',
            '30': 'new_eng_access',
            '32': 'storage_servers',
            '33': 'storage_servers',
            '34': 'storage_servers',
            '35': 'storage_servers',
            '36': 'internal_api',
            '37': 'internal_api',
            '38': 'internal_api',
            '39': 'internal_api',
            '40': 'legacy_util',
            '48': 'management',
            '49': 'management',
            '50': 'management',
            '51': 'management',
            '56': 'physical_infra_drac_pdu',
            '57': 'physical_infra_drac_pdu',
            '58': 'physical_infra_drac_pdu',
            '59': 'physical_infra_drac_pdu',
            '60': 'physical_infra_drac_pdu',
            '61': 'physical_infra_drac_pdu',
            '62': 'physical_infra_drac_pdu',
            '63': 'physical_infra_drac_pdu',
            '64': 'database_servers',
            '65': 'database_servers',
            '66': 'database_servers',
            '67': 'database_servers',
            '72': 'convert_servers',
            '73': 'convert_servers',
            '74': 'convert_servers',
            '75': 'convert_servers',
            '80': 'app_util_servers',
            '81': 'app_util_servers',
            '82': 'app_util_servers',
            '83': 'app_util_servers',
            '88': 'app_backend_servers',
            '89': 'app_backend_servers',
            '90': 'app_backend_servers',
            '91': 'app_backend_servers',
            '92': 'iks_servers',
            '96': 'dwh_cluster_hadoop',
            '97': 'dwh_cluster_hadoop',
            '98': 'dwh_cluster_hadoop',
            '99': 'dwh_cluster_hadoop',
            '103': 'dmz_not_tagged',
            '104': 'dmz_not_tagged',
            '105': 'kickstart',
            '121': 'traffic_manager',
            '124': 'web_proxy',
            '125': 'ftp_frontends',
            '127': 'bastion',
            '128': 'physical_infra_drac_pdu',
            '129': 'physical_infra_drac_pdu',
            '130': 'physical_infra_drac_pdu',
            '131': 'physical_infra_drac_pdu',
            '132': 'physical_infra_drac_pdu',
            '133': 'physical_infra_drac_pdu',
            '134': 'physical_infra_drac_pdu',
            '135': 'physical_infra_drac_pdu',
        }

        g3_vlan_list = {
            '0': {'name': 'network_infrastructure', 'mask': 27},
            '1': {'name': 'boxfiler_and_storage', 'mask': 27},
            '2': {'name': 'alf_servers', 'mask': 27},
            '3': {'name': 'internal_api', 'mask': 27},
            '4': {'name': 'convert_servers', 'mask': 27},
            '5': {'name': 'misc_backend_services', 'mask': 27},
            '6': {'name': 'data_warehouse', 'mask': 27},
            '7': {'name': 'data_warehouse', 'mask': 27},
            '8': {'name': 'database', 'mask': 27},
            '9': {'name': 'management_and_infra', 'mask': 27},
            '10': {'name': 'frontend', 'mask': 27},
            '11': {'name': 'vmh_servers', 'mask': 27},
            '12': {'name': 'pingsso', 'mask': 27},
            '13': {'name': 'iks_keds_backend_security', 'mask': 27},
            '14': {'name': 'notes_frontend', 'mask': 27},
            '15': {'name': 'realtime', 'mask': 27},
            '16': {'name': 'newsroom', 'mask': 27},
            '17': {'name': 'skynet_container_services', 'mask': 27},
            '18': {'name': 'adc_ipvs', 'mask': 27},
            '19': {'name': 'trust_anchor', 'mask': 27},
            '20': {'name': 'openstack_private', 'mask': 26},
            '21': {'name': 'openstack_private', 'mask': 26},
            '22': {'name': 'bastion', 'mask': 27},
            '23': {'name': 'unknown', 'mask': 27},
            '24': {'name': 'calico', 'mask': 27},
            '25': {'name': 'infoblox', 'mask': 27},
            '26': {'name': 'webproxy_and_jumphost', 'mask': 27},
            '27': {'name': 'unknown', 'mask': 27},
            '28': {'name': 'convert', 'mask': 27},
            '29': {'name': 'convert', 'mask': 27},
            '30': {'name': 'frontend', 'mask': 27},
            '31': {'name': 'dmz', 'mask': 27},
            '32': {'name': 'skynet_container', 'mask': 23},
            '33': {'name': 'skynet_container', 'mask': 23},
            '34': {'name': 'skynet_container', 'mask': 23},
            '35': {'name': 'skynet_container', 'mask': 23},
            '36': {'name': 'skynet_container', 'mask': 23},
            '37': {'name': 'skynet_container', 'mask': 23},
            '38': {'name': 'skynet_container', 'mask': 23},
            '39': {'name': 'skynet_container', 'mask': 23},
            '40': {'name': 'skynet_container', 'mask': 23},
            '41': {'name': 'skynet_container', 'mask': 23},
            '42': {'name': 'skynet_container', 'mask': 23},
            '43': {'name': 'skynet_container', 'mask': 23},
            '44': {'name': 'skynet_container', 'mask': 23},
            '45': {'name': 'skynet_container', 'mask': 23},
            '46': {'name': 'skynet_container', 'mask': 23},
            '47': {'name': 'skynet_container', 'mask': 23},
            '48': {'name': 'internal_api', 'mask': 25},
            '49': {'name': 'internal_api', 'mask': 25},
            '50': {'name': 'internal_api', 'mask': 25},
            '51': {'name': 'internal_api', 'mask': 25},
            '52': {'name': 'frontend', 'mask': 25},
            '53': {'name': 'frontend', 'mask': 25},
            '54': {'name': 'frontend', 'mask': 25},
            '55': {'name': 'frontend', 'mask': 25},
            '56': {'name': 'unknown', 'mask': 27},
            '57': {'name': 'unknown', 'mask': 27},
            '58': {'name': 'unknown', 'mask': 27},
            '59': {'name': 'unknown', 'mask': 27},
            '60': {'name': 'cab_local_shit', 'mask': 27},
            '61': {'name': 'cab_local_shit', 'mask': 27},
            '62': {'name': 'kickstart', 'mask': 26},
            '63': {'name': 'kickstart', 'mask': 26},
        }

        edc_seczone_dict = {
            '0': 'network_infra',
            '1': 'ipvs-load-balancers-for-public-product',
            '2': 'ipvs-load-balancers-for-vip-product',
            '3': 'external-egress-nat-service',
            '4': 'gen-ftp-servers',
            '5': 'gen-ftp-servers-for-vip',
            '6': 'gen-oob-bastion-and-utility-hypervisor',
            '7': 'unknown',
            '8': 'unknown',
            '9': 'management-and-infrastructure',
            '10': 'unknown',
            '11': 'unknown',
            '12': 'unknown',
            '13': 'cabinet-local-network',
            '14': 'server-hotcache',
            '15': 'kickstart-network',
        }

        for ip in ips:
            #G2 breakdown
            if ip.site == 'g2':
                second_octet = str(ip).split('.')[1]
                third_octet = str(ip).split('.')[2]

                # 10.25.0.0/16 is AWS Data Platform dev/staging
                if second_octet == '25':
                    if 0 <= int(third_octet) <= 127:
                        bucket['g2']['aws_data_platform']['dev'].append(ip)
                    else:
                        bucket['g2']['aws_data_platform']['staging'].append(ip)
                # "normal" g2 breakdown using the vlan list
                else:
                    btype = g2_vlan_list.get(third_octet, 'unknown')
                    bucket['g2']['compute'][btype].append(ip)

            #G3 breakdown
            elif ip.site in ['csv2', 'esv2', 'slv8', 'vsv1']:
                fields = [8, 4, 5, 4, 6, 5]
                dood = BitDoodle(fields)
                vals = dood.disjoin(int(ip))
                podid = vals[2]
                cabid = vals[3]
                seczone = vals[4]
                hostid = vals[5]
                realipnet = netaddr.IPNetwork('{}/{}'.format(str(ip), '27'))

                # Let's check if seczone is a non /27
                mask = g3_vlan_list.get(str(seczone), 'unknown')['mask']
                if mask <= 26:
                    vlanbitsoffset = (mask - 27)
                    hostbitsoffset = abs(vlanbitsoffset)
                    realipnet = netaddr.IPNetwork('{}/{}'.format(str(ip), str(27 + vlanbitsoffset)))
                    fields = [8, 4, 5, 4, 6 + vlanbitsoffset, 5 + hostbitsoffset]
                    dood = BitDoodle(fields)
                    vals = dood.disjoin(int(ip))
                    # get the new "real" hostid, that can now be >= 32
                    hostid = vals[5]

                # this shit should be compute
                if 1 <= podid <= 29 and 1 <= cabid <= 12:
                    if 4 <= hostid <= realipnet.size:
                        btype = g3_vlan_list.get(str(seczone), 'unknown')['name']
                        bucket['g3']['compute'][btype].append(ip)
                    elif 0 <= hostid <= 3:
                        bucket['g3']['compute']['tsw_vlan_ip'].append(ip)
                elif podid == 0 or cabid == 0:
                        bucket['g3']['network_infra'].append(ip)
                elif podid >= 30:
                    fields = [8, 4, 5, 9, 6]
                    dood = BitDoodle(fields)
                    vals = dood.disjoin(int(ip))
                    oobnet = vals[3]
                    hostid = vals[4]
                    if oobnet == 0:
                        bucket['g3']['oob']['network_infra'].append(ip)
                    elif 1 <= oobnet <= 360:
                        if hostid == 57 or hostid == 58:
                            bucket['g3']['oob']['pdu'].append(ip)
                        elif hostid <= 6:
                            bucket['g3']['oob']['network_infra'].append(ip)
                        else:
                            bucket['g3']['oob']['dracs'].append(ip)
                    elif 494 <= oobnet <= 503:
                        bucket['g3']['oob']['network_infra'].append(ip)
                else:
                    bucket['g3']['unknown'].append(ip)

            #EDC Breakdown
            elif ip.site in ['small_sites/edc']:
                fields = [8, 4, 6, 4, 4, 6]
                dood = BitDoodle(fields)
                vals = dood.disjoin(int(ip))
                smallsite = vals[2]
                cabid = vals[3]
                seczone = vals[4]
                hostid = vals[5]

                # this shit is oob
                if cabid == 15:
                    fields = [8, 4, 6, 4, 4, 6]
                    dood = BitDoodle(fields)
                    vals = dood.disjoin(int(ip))
                    oobnet = vals[4]
                    hostid = vals[5]
                    if oobnet == 0:
                        bucket['edc']['oob']['network_infra'].append(ip)
                    elif 1 <= oobnet <= 4:
                        if 1 <= hostid <= 3:
                            bucket['edc']['oob']['network_infra'].append(ip)
                        elif hostid == 4 or hostid == 5:
                            bucket['edc']['oob']['pdu'].append(ip)
                        else:
                            bucket['edc']['oob']['dracs'].append(ip)
                    else:
                        bucket['edc']['oob']['unknown'].append(ip)

                # this shit is infra
                elif cabid == 0:
                    bucket['edc']['network_infra'].append(ip)
                # this shit is compute
                elif 1 <= cabid <= 14:
                    btype = edc_seczone_dict.get(str(seczone), 'unknown')
                    bucket['edc']['compute'][btype].append(ip)
                else:
                    bucket['edc']['unknown'].append(ip)
            else:
                bucket['unknown'].append(ip)

        flat_bucket = IpChecker.flatten(bucket)

        return flat_bucket
