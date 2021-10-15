# Asynch Node Reboot

This script allows for the reboot of nodes via various means.

To use the script you must first export your API key as an OS environmental variable.

Example: export MERAKI_DASHBOARD_API_KEY=093b24e85df15a3e66f1fc359f4c48493eaa1b73


**Requirements**

Meraki SDK (tested on v1.12)

Example: pip install meraki

**Syntax**

The script uses the following options:

*  [-h, --help]     Provides information related to running the script
*  [-i, --infile]   Allows to use a csv file of serial numbers by providing the path to the .csv
*  [-o]             Mandatory; needed for providing the organization ID
  

**Description**

The script will scan all devices in the specified org for any device tags of "*reboot*". It will then, asynchronously, send API calls for rebooting the list of collected devices.

Alternatively, a path to a csv file can be provided at runtime to use a single column of serials (with a "serials" header) to reboot.

A log file will be available in the same directory after the script completes.