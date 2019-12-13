#!/usr/bin/env python

"""
check_rubrik_runway.py

This script gets the current runway remaining in the Rubrik cluster,
and returns a warning if there is less than 180 days, and a critical
alert if there is less than 60 days remaining.

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

class Rubrikrunway(nagiosplugin.Resource):
    """Rubrik CDM Runway Remaining
    Returns the number of days of runway remaining on the Rubrik CDM cluster
    """

    def __init__(self, rubrik_ip, rubrik_user, rubrik_pass):
        self.rubrik_ip = rubrik_ip
        self.rubrik_user = rubrik_user
        self.rubrik_pass = rubrik_pass

    @property
    def name(self):
        return 'RUBRIK_RUNWAY'

    def get_runway(self):
        """Gets runway remaining metric from Rubrik CDM"""
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        rk = rubrik_cdm.Connect(node_ip=self.rubrik_ip,username=self.rubrik_user,password=self.rubrik_pass)
        rkrunway = rk.get('internal','/stats/runway_remaining')['days']
        return(rkrunway)

    def probe(self):
        rk_runway = self.get_runway()
        _log.debug('RUBRIK REST call returned "%s"', rk_runway)
        rk_runway = int(rk_runway)
        metric = nagiosplugin.Metric('Days remaining', rk_runway, min=0, context='rk_runway')
        return metric

def parse_args():
    argp = argparse.ArgumentParser()
    argp.add_argument('-s', '--rubrik_ip', help="Rubrik hostname or ip address")
    argp.add_argument('-u', '--rubrik_user', help="Rubrik username")
    argp.add_argument('-p', '--rubrik_pass', help="Rubrik password")
    argp.add_argument('-w', '--warning', metavar='RANGE', default='180:', help='return warning if occupancy is outside RANGE. Value is expressed in days')
    argp.add_argument('-c', '--critical', metavar='RANGE', default='60:', help='return critical if occupancy is outside RANGE. Value is expressed in days')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30,
                      help='abort execution after TIMEOUT seconds')
    return argp.parse_args()

@nagiosplugin.guarded
def main():
    args = parse_args()
    check = nagiosplugin.Check( Rubrikrunway(args.rubrik_ip, args.rubrik_user, args.rubrik_pass) )
    check.add(nagiosplugin.ScalarContext('rk_runway', (args.warning+':'), (args.critical+':')))
    check.main(args.verbose, args.timeout)

if __name__ == '__main__':
    main()