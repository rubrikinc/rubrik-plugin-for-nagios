#!/usr/bin/env python

import argparse
import logging
import nagiosplugin
import rubrik_cdm
import urllib3

_log = logging.getLogger('nagiosplugin')

class Rubrikclusterstorage(nagiosplugin.Resource):
    """Rubrik CDM Cluster Storage
    Returns the cluster storage status Rubrik CDM cluster
    """

    def __init__(self, rubrik_ip, rubrik_user, rubrik_pass):
        self.rubrik_ip = rubrik_ip
        self.rubrik_user = rubrik_user
        self.rubrik_pass = rubrik_pass

    @property
    def name(self):
        return 'RUBRIK_CLUSTER_STORAGE'

    def get_cluster_storage(self):
        """Gets cluster storage from Rubrik CDM"""
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        rk = rubrik_cdm.Connect(node_ip=self.rubrik_ip,username=self.rubrik_user,password=self.rubrik_pass)
        rkstorage = rk.get('internal','/stats/system_storage')
        return(rkstorage)

    def probe(self):
        rk_cluster_storage = self.get_cluster_storage()
        rk_total_storage = rk_cluster_storage['total']
        rk_available_storage = rk_cluster_storage['available']
        rk_percent_used = int(float(rk_available_storage) / float(rk_total_storage) * 100)
        _log.debug('Cluster storage is '+str(rk_percent_used)+'% used')
        metric = nagiosplugin.Metric('Cluster used storage', rk_percent_used, '%', min=0, max=100, context='rk_cluster_used')
        return metric

def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument('-s', '--rubrik_ip', help="Rubrik hostname or ip address")
    argp.add_argument('-u', '--rubrik_user', help="Rubrik username")
    argp.add_argument('-p', '--rubrik_pass', help="Rubrik password")
    argp.add_argument('-w', '--warning', metavar='RANGE', default=':50', help='return warning if occupancy is outside RANGE. Value is expressed in percentage')
    argp.add_argument('-c', '--critical', metavar='RANGE', default=':70', help='return critical if occupancy is outside RANGE. Value is expressed in percentage')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()

@nagiosplugin.guarded
def main():
    args = parse_args()
    check = nagiosplugin.Check( Rubrikclusterstorage(args.rubrik_ip, args.rubrik_user, args.rubrik_pass) )
    check.add(nagiosplugin.ScalarContext('rk_cluster_used', args.warning, args.critical))
    check.main(args.verbose, args.timeout)

if __name__ == '__main__':
    main()