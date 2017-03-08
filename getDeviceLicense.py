
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


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))



# The function will generate the Auth ticket required to access APIC-EM
# The function will return the Auth ticket, if successful

def get_service_ticket():
    ticket = None
    payload = {'username': CONTROLLER_USER,'password': CONTROLLER_PASSW}
    url = 'https://' + CONTROLLER_URL + '/ticket'
    header = {'content-type': 'application/json'}
    ticket_response = requests.post(url,data = json.dumps(payload), headers = header, verify = False)
    if not ticket_response:
        print ('Something went wrong, try again!')
    else:
        ticket_json = ticket_response.json()
        ticket = ticket_json['response']['serviceTicket']
        print ('APIC-EM ticket: ', ticket)    # print the ticket for reference only, not required
        return ticket


# The function will find out the active licenses of the network device with the specified device ID
# The function will require two values, the device id and the Auth ticket
# The function will return a list with all active licenses of the network device
# API call to sandboxapic.cisco.com/api/v1//license-info/network-device/{id}

def get_license_device (deviceId, ticket):
    license_info = []
    url = 'https://' + CONTROLLER_URL + '/license-info/network-device/' + deviceId
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    payload = {'deviceId': deviceId}
    device_response = requests.get(url, params=payload, headers=header, verify=False)
    if device_response.status_code == 200:
        device_json = device_response.json()
        device_info = device_json['response']
        # pprint(device_info)    # use this for printing info about each device
        for licenses in device_info:
            try:    # required to avoid errors due to some devices, for example Access Points, that do not have an "inuse" license.
                if licenses.get('status') == 'INUSE':
                    new_license = licenses.get('name')
                    if new_license not in license_info:
                        license_info.append(new_license)
            except:
                pass
    else:
        pass
    return license_info


# The function will find out the hostname of the network device with the specified device ID
# The function will require two values, the device id and the Auth ticket
# The function will return a list with the hostname, the device type, and serial number of the network device
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


# The function will ask the user to input the file name to save data to
# The function will append .csv and return the file name with extension

def get_input_file():
    filename = input('Input the file name to save data to:  ') + '.csv'
    return filename


# The function will build the ID's list for all network devices
# The function will require one value, the Auth ticket
# The function will return the device's ID as a list
# API call to sandboxapic.cisco.com/api/v1/network-device

def get_device_Ids(ticket):
    device_Id_list = []
    url = 'https://' + CONTROLLER_URL + '/network-device'
    header = {'accept': 'application/json', 'X-Auth-Token': ticket}
    device_response = requests.get(url, headers=header, verify=False)
    device_json = device_response.json()
    device_info = device_json['response']
    for items in device_info:
        device_id = items.get('id')
        device_Id_list.append(device_id)
    return device_Id_list


# The function will create a list of lists.
# For each device we will have a list that includes - hostname, Serial Number, and active licenses
# The function will require two values, the list with all device Id's and the Auth ticket
# The function will return the list

def collect_device_info (device_Id_list, ticket):
    all_devices_license_file = []
    for device_Id in device_Id_list:    # loop to collect data from each device
        license_file = []
        print ('device Id ', device_Id)    # print device Id, printing messages will show progress
        host_name = get_hostname_devicetype_serialnumber(device_Id, ticket)[0]
        serial_number = get_hostname_devicetype_serialnumber(device_Id, ticket)[2]
        license_file.append(host_name)
        license_file.append(serial_number)
        device_license = get_license_device(device_Id, ticket)    # call the function to provide active licenses
        for licenses in device_license:    # loop to append the provided active licenses to the device list
            license_file.append(licenses)
        all_devices_license_file.append(license_file)    # append the created list for this device to the list of lists
    return all_devices_license_file


# main program

def main():
    ticket = get_service_ticket()    # create an APIC-EM Auth ticket
    device_Id_list = get_device_Ids(ticket)    # build a list with all device Id's
    devices_info = collect_device_info(device_Id_list, ticket)    # create a list of lists. Each list will include hostname, S/N, active licenses
    filename = get_input_file()    # ask user for filename input
    output_file = open(filename, 'w', newline='')
    outputWriter = csv.writer(output_file)
    for lists in devices_info:
        outputWriter.writerow(lists)
    output_file.close()
    # pprint(devices_info)    # print for data validation

if __name__ == '__main__':
    main()
