# Rubrik Nagios/Icinga Plugin

## Overview

This repository contains monitoring scripts for Nagios and Icinga. These are written in Python, the requirements for the Nagios/Icinga server are detailed below.

## Pre-Requisites

The scripts require the following Python modules to operate:

* rubrik_cdm
* nagiosplugin

It has been tested with Python 2.7.

## Scripts

### Cluster Storage

This script is named `check_rubrik_cluster_storage.py` and returns the used storage for the Rubrik cluster. Usage is as follows:

```bash
usage: check_rubrik_cluster_storage.py [-h] [-s RUBRIK_IP] [-u RUBRIK_USER]
                                       [-p RUBRIK_PASS] [-w RANGE] [-c RANGE]
                                       [-v] [-t TIMEOUT]

optional arguments:
  -h, --help            show this help message and exit
  -s RUBRIK_IP, --rubrik_ip RUBRIK_IP
                        Rubrik hostname or ip address
  -u RUBRIK_USER, --rubrik_user RUBRIK_USER
                        Rubrik username
  -p RUBRIK_PASS, --rubrik_pass RUBRIK_PASS
                        Rubrik password
  -w RANGE, --warning RANGE
                        return warning if occupancy is outside RANGE. Value is
                        expressed in percentage
  -c RANGE, --critical RANGE
                        return critical if occupancy is outside RANGE. Value
                        is expressed in percentage
  -v, --verbose         increase output verbosity (use up to 3 times)
  -t TIMEOUT, --timeout TIMEOUT
                        abort execution after TIMEOUT seconds
```

Default thresholds are: Warning at 50% used, Critical at 70% used. These are tunable via the `-w` and `-c` parameters.

Sample output:

```bash
> python check_rubrik_cluster_storage.py -s 'rubrik.demo.com' -u 'admin' -p 'mypass123!'
RUBRIK_CLUSTER_STORAGE WARNING - Cluster used storage is 65% (outside range 0:50) | 'Cluster used storage'=65%;50;70;0;100
```

### Node Status

This script is named `check_rubrik_node_status.py` and returns the health status of nodes in the Rubrik cluster. Usage is as follows:

```bash
usage: check_rubrik_node_status.py [-h] [-s RUBRIK_IP] [-u RUBRIK_USER]
                                   [-p RUBRIK_PASS] [-w RANGE] [-c RANGE] [-v]
                                   [-t TIMEOUT]

optional arguments:
  -h, --help            show this help message and exit
  -s RUBRIK_IP, --rubrik_ip RUBRIK_IP
                        Rubrik hostname or ip address
  -u RUBRIK_USER, --rubrik_user RUBRIK_USER
                        Rubrik username
  -p RUBRIK_PASS, --rubrik_pass RUBRIK_PASS
                        Rubrik password
  -w RANGE, --warning RANGE
                        return warning if occupancy is outside RANGE. Value is
                        expressed in number of unhealthy nodes
  -c RANGE, --critical RANGE
                        return critical if occupancy is outside RANGE. Value
                        is expressed in number of unhealthy nodes
  -v, --verbose         increase output verbosity (use up to 3 times)
  -t TIMEOUT, --timeout TIMEOUT
                        abort execution after TIMEOUT seconds
```

Default thresholds are: Warning at more than 0 unhealthy nodes, Critical at more than 0 unhealthy nodes. These are tunable via the `-w` and `-c` parameters.

Sample output:

```bash
> python check_rubrik_node_status.py -s 'rubrik.demo.com' -u 'admin' -p 'mypass123!'
RUBRIK_NODE_STATUS OK - Unhealthy nodes is 0 | 'Unhealthy nodes'=0;~:0;~:0;0
```

### Runway Remaining

This script is named `check_rubrik_runway.py` and returns the remaining runway in the Rubrik cluster in days. Usage is as follows:

```bash
usage: check_rubrik_runway.py [-h] [-s RUBRIK_IP] [-u RUBRIK_USER]
                              [-p RUBRIK_PASS] [-w RANGE] [-c RANGE] [-v]
                              [-t TIMEOUT]

optional arguments:
  -h, --help            show this help message and exit
  -s RUBRIK_IP, --rubrik_ip RUBRIK_IP
                        Rubrik hostname or ip address
  -u RUBRIK_USER, --rubrik_user RUBRIK_USER
                        Rubrik username
  -p RUBRIK_PASS, --rubrik_pass RUBRIK_PASS
                        Rubrik password
  -w RANGE, --warning RANGE
                        return warning if occupancy is outside RANGE. Value is
                        expressed in days
  -c RANGE, --critical RANGE
                        return critical if occupancy is outside RANGE. Value
                        is expressed in days
  -v, --verbose         increase output verbosity (use up to 3 times)
  -t TIMEOUT, --timeout TIMEOUT
                        abort execution after TIMEOUT seconds
```

Default thresholds are: Warning at 180 days or less remaining, Critical at 60 days or less remaining. These are tunable via the `-w` and `-c` parameters.


Sample output:

```bash
> python check_rubrik_runway.py.py -s 'rubrik.demo.com' -u 'admin' -p 'mypass123!'
RUBRIK_RUNWAY OK - Days remaining is 486 | 'Days remaining'=486;180:;60:;0
```

## Implementing in Icinga

The following template can be used as guidance for defining the command in Icinga:

`/etc/icinga2/conf.d/commands.conf`

```
object CheckCommand "rubrik_runway" {
  import "plugin-check-command"

  command = [ PluginDir + "/check_rubrik_runway" ]

  arguments = {
    "--rubrik_ip" = {
      required = true
      value = "rubrik.demo.com"
    }
    "--rubrik_user" = {
      required = true
      value = "admin"
    }
    "--rubrik_pass" = {
      required = true
      value = "mypass123!"
    }
  }
}
```

`/etc/icinga2/conf.d/services.conf`

```
apply Service "rubrik_runway" {
  check_command = "rubrik_runway"
  assign where host.address
}
```

The script should be copied to the Icinga plugins directory on the machine hosting the Nagios server or the NRPE for example the /usr/lib/nagios/plugins folder. Change the execution rights of the program to allow the execution to 'all' (usually chmod 0755).

## Credentials

The scripts shosld be run as a user with admin credentials on the cluster. From Rubrik CDM 4.2, it is possible to create a read only admin user, which is better suited for this kind of monitoring. To do this, run the following commands:

```bash
USER_ID=$(curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{"username":"readonlyadmin","password":"NotAPa$5123!!!","emailAddress":"readonlyadmin@rubrik.demo"}' 'https://rubrik.demo.com/api/internal/user' -k -u 'admin:NotAPa$5123!!!' -s | jq -r '.id')
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d $(echo '{"principals":["'$USER_ID'"],"privileges":{"basic":["Global:::All"]}}') 'https://rubrik.demo.com/api/internal/authorization/role/read_only_admin' -k -u 'admin:NotAPa$5123!!!' -s | jq
```

This will create a read only admin user with the specified details. This has been tested with the integration and works fine.
