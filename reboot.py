import getopt
import os
import sys
import asyncio
import meraki.aio
import csv

RETRIES = 5 # Max number of retries per call for 429 rate limit status code

READ_ME = '''
The script reboots all devices with the tag "reboot".
Alternatively, a .csv file can be specified to use a list of serials

usage: python3 reboot_script.py [-o] organizationId
       python3 reboot_script.py [-o] organizationId [-i, --infile] path_to_csv
'''


def print_help():
    lines = READ_ME.split('\n')
    for line in lines:
        print(f'# {line}')

async def rebootDevice(aiomeraki: meraki.aio.AsyncDashboardAPI, device):
    try:
        await aiomeraki.devices.rebootDevice(device['serial'])
    except meraki.AsyncAPIError as e:
        print(f'Meraki API error for {device[0]}: {e}')
    except Exception as e:
        print(f'The following error has occurred: {e}')


async def listDevicesFromFile(file):
    with open(file) as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')
        next(csvReader)
        try:
            taggedDevices = []
            for row in csvReader:
                taggedDevices.append({"serial": row[0]})
        except csv.Error as e:
            sys.exit(f'file {file}, line {csvReader.line_num}: {e}')
    return taggedDevices


async def listOrgDevices(aiomeraki: meraki.aio.AsyncDashboardAPI, org_id_num):
    try:
        devices = await aiomeraki.organizations.getOrganizationDevices(org_id_num)
    except meraki.AsyncAPIError as e:
        print(f'Meraki API error: {e}')
    except Exception as e:
        print(f'The following error has occurred: {e}')
    taggedDevices = []
    for device in devices:
        if "reboot" in (tag.lower() for tag in device['tags']):
            taggedDevices.append(device)

    return taggedDevices



async def main(argv):
    use_file = False
    try:
        opts, args = getopt.getopt(argv, "ho:i:", ["help", "infile="])
        if not (2 <= len(sys.argv[1:]) <= 4):
            print('****** # ERROR: Incorrect number of parameters given ******')
            print_help()
            sys.exit()
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        if opt in ("-i", "--infile"):
            file_path = arg
            use_file = True
        elif opt == "-o":
            org_id = arg
        else:
            print_help()
            sys.exit(2)

    async with meraki.aio.AsyncDashboardAPI(
        log_file_prefix=__file__[:-3],
        print_console= False,
        maximum_retries= RETRIES
    ) as aiomeraki:
        # Get org details
        try:
            org = await aiomeraki.organizations.getOrganization(org_id)
        except meraki.AsyncAPIError as e:
            print(f'Meraki API error: {e}')
            return org_id
        except Exception as e:
            print(f'The following error has occurred: {e}')
            return org_id
        # Create list of devices that are tagged to be rebooted
        print(f'Acquiring device list from the organization {org["name"]}')
        if use_file:
            print('CSV file selected to use as input for devices to reboot...')
            devices = await listDevicesFromFile(file_path)
        else:
            print('Primary option of device tags will be used for device reboot...')
            devices = await listOrgDevices(aiomeraki, org_id)

        total = len(devices)
        print(f'Found {total} devices to be rebooted')

        print('Reboot of devices in progress....')
        deviceTasks = [rebootDevice(aiomeraki, device) for device in devices]
        for task in asyncio.as_completed(deviceTasks):
            await task

        print(f'Reboot of all {total} devices completed!!!')


if __name__ == "__main__":
    import time
    s = time.perf_counter()
    asyncio.run(main(sys.argv[1:]))
    elapsed = time.perf_counter() - s
    print(f'Reboot script took {elapsed:0.2f} seconds to complete.')