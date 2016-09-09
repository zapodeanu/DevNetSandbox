
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
    payload = {'username': CONTROLLER_USER, 'password': CONTROLLER_PASSW}
    url = 'https://' + CONTROLLER_URL + '/ticket'
    header = {'content-type': 'application/json'}
    ticket_response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    if not ticket_response:
        print ('No data returned!')
    else:
        ticket_json = ticket_response.json()
        ticket = ticket_json['response']['serviceTicket']
        print ('APIC-EM ticket: ', ticket)
        return ticket


# This function will ask the user to input the IP address to be validated
# The function will return the IP address

def get_input_IP():
    interfaceIP = None
    interfaceIP = input('What is the IP address?  ')
    return interfaceIP


# The function will find out if APIC-EM has a client device configured with the specified IP address
# The function will require two values, the Auth ticket and the IP address
# The function will return the network device name and the interface the client is connected to

def check_client_IP_address(clientIP, ticket):
    interfaceName = None
    hostname = None
    host_info = None
    url = 'https://' + CONTROLLER_URL + '/host'
    header = {'content-type': 'application/json', 'X-Auth-Token': ticket}
    payload = {'hostIp': clientIP}
    host_response = requests.get(url, params=payload, headers=header, verify=False)
    host_json = host_response.json()
    if host_json['response'] == []:
        print ('The IP address ', clientIP, ' is not used by any client devices')
    else:
        host_info = host_json['response'][0]
        interfaceName = host_info['connectedInterfaceName']
        deviceId = host_info['connectedNetworkDeviceId']
        hostName = get_hostname_id(deviceId, ticket)
        print ('The IP address ', clientIP, ' is connected to the network device ', hostName, ' , interface ', interfaceName)
        return hostName, interfaceName


# The function will find out if APIC-EM has a network device with the specified IP address configured on an interface
# The function will require two values, the Auth ticket and the IP address
# The function will return the interface name and device ID, to be used for future use cases

def get_interface_name(interfaceIP, ticket):
    interfaceInfo = None
    url = 'https://' + CONTROLLER_URL + '/interface/ip-address/' + interfaceIP
    header = {'content-type': 'application/json', 'X-Auth-Token': ticket}
    interfaceInfo_response = requests.get(url, headers=header, verify=False)
    if not interfaceInfo_response:
        print ('The IP address ', interfaceIP, ' is not configured on any network devices')
    else:
        interfaceInfo_json = interfaceInfo_response.json()
#        print (json.dumps(interfaceName_json, indent=4, separators=(' , ', ' : ')))  # print json output, optional, remove the comment from the beginning of the line
        interfaceInfo = interfaceInfo_json['response'][0]
        interfaceName = interfaceInfo['portName']
        deviceId = interfaceInfo['deviceId']
        hostName = get_hostname_id(deviceId, ticket)
        print('The IP address ', interfaceIP, ' is configured on network device ', hostName, ', interface ', interfaceName)
        return hostName, deviceId


# The function will find out the hostname of the network device with the specified device ID
# The function will require two values, the Auth ticket and the device ID
# The function with return the hostname of the network device

def get_hostname_id(deviceId, ticket):
    hostname = None
    url = 'https://' + CONTROLLER_URL + '/network-device/' + deviceId
    header = {'content-type': 'application/json', 'X-Auth-Token': ticket}
    hostname_response = requests.get(url, headers=header, verify=False)
    hostname_json = hostname_response.json()
#    print (json.dumps(hostname_json, indent=4, separators=(' , ', ' : ')))  # print json output, optional, remove the comment from the beginning of the line
    hostname = hostname_json['response']['hostname']
    return hostname


def main():
    ticket = get_service_ticket()
    interfaceIP = get_input_IP()
    check_client_IP_address(interfaceIP, ticket)
    get_interface_name(interfaceIP, ticket)


main()
