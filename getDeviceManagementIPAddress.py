
#!/usr/bin/env python3

import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

# definitions for Sandbox APIC-EM API url, username and password

CONTROLLER_URL = "sandboxapic.cisco.com/api/v1"
CONTROLLER_USER = "devnetuser"
CONTROLLER_PASSW = "Cisco123!"


# This function will generate the Auth ticket required to access APIC-EM
# The function will return the Auth ticket, if successful

def get_service_ticket():
    ticket = None
    payload = {"username": CONTROLLER_USER,"password": CONTROLLER_PASSW}
    url = "https://" + CONTROLLER_URL + "/ticket"
    header = {"content-type": "application/json"}
    ticket_response = requests.post(url,data = json.dumps(payload), headers = header, verify = False)
    if not ticket_response:
        print ("No data returned!")
    else:
        ticket_json = ticket_response.json()
        ticket = ticket_json["response"]["serviceTicket"]
        print ("APIC-EM ticket: ", ticket)    # print the ticket for reference only, not required
        return ticket


# This function will ask the user to input the device management IP address
# The function will return the IP address

def get_input_IP():
    deviceIP = None
    deviceIP = input("What is the device management IP address?  ")
    return deviceIP


# The function will find out if APIC-EM has a network device with the specified management IP address
# The function will require two values, the Auth ticket and the device management IP address
# The function will return the device hostname

def get_hostname(deviceIP, ticket):
    hostname = None
    url = "https://" + CONTROLLER_URL + "/network-device/ip-address/" + deviceIP
    header = {"content-type": "application/json", "X-Auth-Token":ticket}
    hostname_response = requests.get(url, headers = header, verify = False)
    if not hostname_response:
        print ("No device with this management IP address!")
    else:
        hostname_json = hostname_response.json()
#        print (json.dumps(hostname_json, indent=4, separators=(" , ", " : ")))  # print json output, optional, remove the comment from the beginning of the line
        hostname = hostname_json["response"]["hostname"]
        print ("Device Hostname:  ", hostname)
        return hostname


def main():
    ticket = get_service_ticket()
    deviceIP = get_input_IP()
    get_hostname(deviceIP, ticket)


main()

