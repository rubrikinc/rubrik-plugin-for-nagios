#!/usr/bin/env python

# Copyright 2018 Rubrik, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import argparse
import logging
import urllib3

import nagiosplugin
import rubrik_cdm


_log = logging.getLogger('nagiosplugin')


class RubrikClusterStorage(nagiosplugin.Resource):
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

        rk = rubrik_cdm.Connect(node_ip=self.rubrik_ip, username=self.rubrik_user, password=self.rubrik_pass)
        storage = rk.get('internal', '/stats/system_storage')

        return storage

    def probe(self):
        cluster_storage = self.get_cluster_storage()

        total_storage = cluster_storage['total']
        available_storage = cluster_storage['available']
        
        percent_used = 100 - int(float(available_storage) / float(total_storage) * 100)
        _log.debug(f'Cluster storage is {percent_used}% used')

        metric = nagiosplugin.Metric('Cluster used storage', percent_used, '%', min=0, max=100, context='rk_cluster_used')

        return metric


def parse_args():
    argp = argparse.ArgumentParser()

    argp.add_argument('-s', '--rubrik_ip', help="Rubrik hostname or ip address")
    argp.add_argument('-u', '--rubrik_user', help="Rubrik username")
    argp.add_argument('-p', '--rubrik_pass', help="Rubrik password")
    argp.add_argument('-w', '--warning', metavar='RANGE', default=':50', help='return warning if occupancy is outside RANGE. Value is expressed in percentage')
    argp.add_argument('-c', '--critical', metavar='RANGE', default=':70', help='return critical if occupancy is outside RANGE. Value is expressed in percentage')
    argp.add_argument('-v', '--verbose', action='count', default=0, help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=30, help='abort execution after TIMEOUT seconds')

    return argp.parse_args()


@nagiosplugin.guarded
def main():
    args = parse_args()
    check = nagiosplugin.Check(RubrikClusterStorage(args.rubrik_ip, args.rubrik_user, args.rubrik_pass))
    check.add(nagiosplugin.ScalarContext('rk_cluster_used', args.warning, args.critical))
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
