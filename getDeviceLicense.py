
#!/usr/bin/env python3

import requests
import json
import csv
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


# The function will find out the active licenses of the network device with the specified device ID
# The function will require two values, the Auth ticket and device id
# The function with return a list with all active licenses of the network device
# API call to sandboxapic.cisco.com/api/v1//license-info/network-device/{id}

def get_license_device (deviceId, ticket):
    licenseInfo = []
    url = 'https://' + CONTROLLER_URL + '/license-info/network-device/' + deviceId
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    payload = {'deviceId': deviceId}
    device_response = requests.get(url, params=payload, headers=header, verify=False)
    device_json = device_response.json()
    device_info = device_json['response']
    for licenses in device_info:
        try:
            if licenses.get('status') == "INUSE":
                new_license = licenses.get('name')
                if new_license not in licenseInfo:
                    licenseInfo.append(new_license)
        except:
            pass
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


# This function will ask the user to input the file name to save data to
# The function will return the file name, after appending .csv

def get_input_file():
    filename = input('Input the file name to save data to:  ') + '.csv'
    return filename


# The function will build a list of ID's for all network devices
# The function will require one value, the Auth ticket
# The function with return the device's ID as a list
# API call to sandboxapic.cisco.com/api/v1/network-device

def get_device_Ids(ticket):
    deviceIdList = []
    url = 'https://' + CONTROLLER_URL + '/network-device'
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    device_response = requests.get(url, headers=header, verify=False)
    device_json = device_response.json()
    device_info = device_json['response']
    for items in device_info:
        device_id = items.get('id')
        deviceIdList.append(device_id)
    return deviceIdList


# The function will create a list with a row for each device hostname, Serial Number, Licenses
# The function will require two values, the list with all device Id's and the Auth ticket
# The function with return list with a row for each device

def collect_device_info (device_Id_list, ticket):
    all_devices_license_file = []
    for device_Id in device_Id_list:    # loop to collect data from each device
        license_file = []
        print ('device Id ', device_Id)    # print device Id, printing messages will show progress
        host_name = get_hostname_devicetype_serialnumber(device_Id, ticket)[0]
        serial_number = get_hostname_devicetype_serialnumber(device_Id, ticket)[2]
        license_file.append(host_name)
        license_file.append(serial_number)
        devicelicense = get_license_device(device_Id, ticket)
        for licenses in devicelicense:
            license_file.append(licenses)
        all_devices_license_file.append(license_file)
#    print(json.dumps(all_devices_license_file, indent=4, separators=(' , ', ' : ')))
    return all_devices_license_file


# main program

def main():
    ticket = get_service_ticket()
    device_Id_list = get_device_Ids(ticket)
    devices_info = collect_device_info(device_Id_list, ticket)
    filename = get_input_file()
    outputFile = open(filename, 'w', newline='')
    outputWriter = csv.writer(outputFile)
    for lists in devices_info:
        outputWriter.writerow(lists)
    outputFile.close()
    print (devices_info)

if __name__ == '__main__':
    main()
