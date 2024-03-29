#!/usr/bin/env python3


# developed by Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems


import time
import urllib3
import logging

import dnac_apis
import service_now_apis

from requests.auth import HTTPBasicAuth  # for Basic Auth
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

from config import DNAC_PASS, DNAC_USER
from config import PnP_WLC_NAME
from config import SNOW_DEV
from config import AP_ASSIGN_SITE

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)


def main():
    """
    - identify any PnP unclaimed APs
    - map to local database to identify the floor to be provisioned to
    - claim the device
    - verify PnP process workflow
    - re-sync the WLC controller
    - verify the AP on-boarded using the Cisco DNA Center Inventory
      - reachability, IP address, access switch info, WLC info
    - create, update a ServiceNow incident with the information
    - close ServiceNow incident if PnP completes successfully
    """

    # run the application on demand, scanning for a new device in the Cisco DNA Center PnP Provisioning tab

    print('\n\nApplication "dnac_pnp_ap.py" started')

    # device info and site

    pnp_device_assign = AP_ASSIGN_SITE

    site_name = pnp_device_assign['site_name']
    floor_name = pnp_device_assign['floor_name']
    pnp_device_name = pnp_device_assign['device_hostname']

    print('\nThis application will assign the device \n', pnp_device_name,
          ' to the site: ', pnp_device_assign['site_name'] + ' / ' + floor_name)

    # logging, debug level, to file {application_run.log}
    logging.basicConfig(
        filename='application_run.log',
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    dnac_token = dnac_apis.get_dnac_jwt_token(DNAC_AUTH)

    # check if any devices in 'Unclaimed' and 'Initialized' state, if not wait for 10 seconds and run again
    pnp_unclaimed_device_count = 0
    while pnp_unclaimed_device_count == 0:
        try:
            pnp_unclaimed_device_count = dnac_apis.pnp_get_device_count('Unclaimed', dnac_token)
            if pnp_unclaimed_device_count != 0:

                # get the pnp device info
                pnp_devices_info = dnac_apis.pnp_get_device_list(dnac_token)
                device_state = pnp_devices_info[0]['deviceInfo']['state']
                device_onb_state = pnp_devices_info[0]['deviceInfo']['onbState']

                # verify if device is ready to be claimed: state = Unclaimed "and" onboard_state = Initialized
                if device_state == 'Unclaimed' and device_onb_state == 'Initialized':
                    break
                else:
                    pnp_unclaimed_device_count = 0
        except:
            pass
        time.sleep(10)

    print('\nFound Unclaimed PnP devices count: ', pnp_unclaimed_device_count)

    pnp_device_id = pnp_devices_info[0]['id']

    comment = '\nUnclaimed PnP device info:'
    comment += '\nPnP Device Hostname: ' + pnp_device_name
    comment += '\nPnP Device Id: ' + pnp_device_id
    
   # get the floor id to assign device to using pnp

    floor_id = dnac_apis.get_floor_id(site_name, 'Floor 1', dnac_token)
    print('Floor Id: ', floor_id)

    print('\nAP PnP Provisioning Started (this may take few minutes)')

    # start the claim process of the device to site
    claim_result = dnac_apis.pnp_claim_ap_site(pnp_device_id, floor_id, 'TYPICAL', dnac_token)
    #comment = '\nClaim Result: ' + claim_result

    # check claim status every 5 seconds, build a progress status list, end when state == provisioned, exit
    status_list = []
    claim_status = dnac_apis.pnp_get_device_info(pnp_device_id, dnac_token)['state']
    status_list.append(claim_status)

    while claim_status != 'Provisioned':
        claim_status = dnac_apis.pnp_get_device_info(pnp_device_id, dnac_token)['state']
        if claim_status not in status_list:
            status_list.append(claim_status)
        time.sleep(5)

    comment = ''
    for status in status_list:
        comment += '\nPnP Device State: ' + status

    # collect AP info
    ap_device_id = dnac_apis.get_device_id_name(pnp_device_name, dnac_token)
    ap_device_info = dnac_apis.get_device_info(ap_device_id, dnac_token)
    ap_reachability = ap_device_info['reachabilityStatus']
    ap_controller_ip = ap_device_info['associatedWlcIp']
    ap_ip_address = ap_device_info['managementIpAddress']
    ap_device_location = dnac_apis.get_device_location(pnp_device_name, dnac_token)
    ap_access_switch_info = dnac_apis.get_physical_topology(ap_ip_address, dnac_token)
    ap_access_switch_hostname = ap_access_switch_info[0]
    ap_access_switch_port = ap_access_switch_info[1]

    # collect WLC info
    wlc_info = dnac_apis.get_device_info_ip(ap_controller_ip, dnac_token)
    wlc_hostname = wlc_info['hostname']

    comment = '\nProvisioned Access Point Info:\n - Reachability: ' + ap_reachability
    comment += '\n - IP Address: ' + ap_ip_address
    comment += '\n - Connected to: ' + ap_access_switch_hostname + ' , Interface: ' + ap_access_switch_port
    comment += '\n - Location: ' + ap_device_location
    comment += '\n - WLC Controller: ' + wlc_hostname + ' , IP Address: ' + ap_controller_ip

    print('\n\nAP PnP provisoning completed')


if __name__ == '__main__':
    main()
