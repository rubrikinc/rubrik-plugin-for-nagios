#!/usr/bin/env python

"""
check_rubrik_node_status.py

This script gets the status for all nodes in the Rubrik cluster,
and returns a critical alert if any node has a status other than
OK.

Requires the following non-core Python modules:
- nagiosplugin
- rubrik_cdm
These are both avaialble from PyPI via pip

Installation:

The script should be copied to the Nagios plugins directory on the machine hosting the Nagios server or the NRPE
for example the /usr/lib/nagios/plugins folder.
Change the execution rights of the program to allow the execution to 'all' (usually chmod 0755).

Created by Tim Hynes at Rubrik
"""
import argparse
import logging
import nagiosplugin
import rubrik_cdm
import urllib3

_log = logging.getLogger('nagiosplugin')

class Rubriknodestatus(nagiosplugin.Resource):
    """Rubrik CDM Node Status
    Returns the status of all nodes in the Rubrik CDM cluster
    """

    def __init__(self, rubrik_ip, rubrik_user, rubrik_pass):
        self.rubrik_ip = rubrik_ip
        self.rubrik_user = rubrik_user
        self.rubrik_pass = rubrik_pass

    @property
    def name(self):
        return 'RUBRIK_NODE_STATUS'

    def get_node_status(self):
        """Gets node statuses from Rubrik CDM"""
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        rk = rubrik_cdm.Connect(node_ip=self.rubrik_ip,username=self.rubrik_user,password=self.rubrik_pass)
        rknodes = rk.get('internal','/node')
        return(rknodes)

    def probe(self):
        rk_node_status = self.get_node_status()
        rk_number_of_nodes = rk_node_status['total']
        rk_bad_nodes = 0
        rk_nodes = rk_node_status['data']
        rk_status = 'OK'
        for rk_node in rk_nodes:
            rk_node_status = rk_node['status']
            if rk_node_status != 'OK':
                rk_status = rk_node_status
                rk_bad_nodes = rk_bad_nodes + 1
        if rk_status == 'OK':
            _log.debug('All '+str(rk_number_of_nodes)+' nodes are in an OK status')
        else:
            _log.debug(str(rk_bad_nodes)+' returned an unhealthy status')

        metric = nagiosplugin.Metric('Unhealthy nodes', rk_bad_nodes, min=0, context='rk_bad_nodes')
        return metric

def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument('-s', '--rubrik_ip', help="Rubrik hostname or ip address")
    argp.add_argument('-u', '--rubrik_user', help="Rubrik username")
    argp.add_argument('-p', '--rubrik_pass', help="Rubrik password")
    argp.add_argument('-w', '--warning', metavar='RANGE', default='~:0', help='return warning if occupancy is outside RANGE. Value is expressed in number of unhealthy nodes')
    argp.add_argument('-c', '--critical', metavar='RANGE', default='~:0', help='return critical if occupancy is outside RANGE. Value is expressed in number of unhealthy nodes')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()

@nagiosplugin.guarded
def main():
    args = parse_args()
    check = nagiosplugin.Check( Rubriknodestatus(args.rubrik_ip, args.rubrik_user, args.rubrik_pass) )
    check.add(nagiosplugin.ScalarContext('rk_bad_nodes', args.warning, args.critical))
    check.main(args.verbose, args.timeout)

if __name__ == '__main__':
    main()