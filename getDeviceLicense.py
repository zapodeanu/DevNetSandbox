
#!/usr/bin/env python3

import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

# definitions for Sandbox APIC-EM API url, username and password

CONTROLLER_URL = 'sandboxapic.cisco.com/api/v1'
CONTROLLER_USER = 'devnetuser'
CONTROLLER_PASSW = 'Cisco123!'


# This function will generate the Auth ticket required to access APIC-EM
# The function will return the Auth ticket, if successful

def get_service_ticket():
    ticket = None
    payload = {'username': CONTROLLER_USER,'password': CONTROLLER_PASSW}
    url = 'https://' + CONTROLLER_URL + '/ticket'
    header = {'content-type': 'application/json'}
    ticket_response = requests.post(url,data = json.dumps(payload), headers = header, verify = False)
    if not ticket_response:
        print ('No data returned!')
    else:
        ticket_json = ticket_response.json()
        ticket = ticket_json['response']['serviceTicket']
        print ('APIC-EM ticket: ', ticket)    # print the ticket for reference only, not required
        return ticket

# definition for a test deviceId
deviceId = '80036c7d-c82e-412c-ac01-b05f9badfcba'


# The function will find out the active licenses of the network device with the specified device ID
# The function will require two values, the Auth ticket and device id
# The function with return a list with all active licenses of the network device
# API call to sandboxapic.cisco.com/api/v1//license-info/network-device/{id}

def get_license_device (deviceId, ticket):
    url = 'https://' + CONTROLLER_URL + '/license-info/network-device/' + deviceId
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    payload = {'deviceId': deviceId}
    device_response = requests.get(url, params=payload, headers=header, verify=False)
    device_json = device_response.json()
    licenseIndex = int(0)
    licenseInfo = []
    try:
        while licenseIndex < 20:
            device_info= device_json['response'][licenseIndex]
            if device_info['status'] == "INUSE":
                licenseInfo.append(device_info['name'])
#                print ('device JSON  ', device_info)    # print license info for each device, optional or for troubleshooting
            licenseIndex = licenseIndex + 1
    except:
#        print ('This device has ', licenseIndex, 'possible licenses', ', Active licenses on this device: ', licenseInfo)    # this is for troubleshooting
        return licenseInfo


# The function will find out the hostname of the network device with the specified device ID
# The function will require two values, the Auth ticket and device id
# The function with return the hostname, the device type, and serial number of the network device
# API call to sandboxapic.cisco.com/api/v1/network-device/{id}

def get_hostname_devicetype_serialnumber(deviceId, ticket):
    hostname = None
    url = 'https://' + CONTROLLER_URL + '/network-device/' + deviceId
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    hostname_response = requests.get(url, headers=header, verify=False)
    hostname_json = hostname_response.json()
    hostname = hostname_json['response']['hostname']
    devicetype =  hostname_json['response']['type']
    serialnumber = hostname_json['response']['serialNumber']
    return hostname, devicetype, serialnumber


# main program

def main():
    ticket = get_service_ticket()
    license = get_license_device(deviceId, ticket)
    host_name = get_hostname_devicetype_serialnumber(deviceId, ticket)[0]
    device_type = get_hostname_devicetype_serialnumber(deviceId, ticket)[1]
    serial_number = get_hostname_devicetype_serialnumber(deviceId, ticket)[2]
    print ('This network device ', host_name, ', model ', device_type, ', with S/N ', serial_number, ', has these active licenses ', license)


if __name__ == '__main__':
    main()
