# PnP_AP_Provisioning
PnP AP Provisioning via Cisco Catalyst Center


This repo includes all the files needed for PnP AP Provisioning.
This application has been tested using Cisco DNA Center version 1.2.10, C9800-CL controller version 16.10, and one Access Point Cisco 3800.

For the application the following are needed:
- Cisco DNA Center
- Catalyst 9800 controller
- Cisco Access Point 3800


## Installation

The requirements.txt file includes all the Python libraries needed for this application.


## Configuration

Change the config.py file with the devices, applications, user name and passwords that you have in your environment.
This file is the only file you need to change.

## Usage

Files included:
 - requirements.txt - python libraries required
 - config.py - file with the info on how to configure access to devices and applications, and the AP assignment
 - dnac_apis.py, service_now_apis.py - Python modules for DNA Center and ServiceNow
 - utils.py - Python module with various Python useful tools
 - dnac_pnp_ap.py - AP PnP provisioning
 - dnac_pnp_ap_reset.py - reset AP PnP demo
   

This sample application was developed in Python and requires Cisco Catalyst Center, Cisco Wireless LAN Controllers. The application's roadmap includes automated Access Point (AP) assignment to site/floor.

The Challenge:
•	Mass Access Points deployment
•	Ongoing large wireless hardware refresh
•	Time required to provision Access Points

The Goal:
•	Automate the workflow to onboard APs so that no Network Engineer time is required.

The Solution:
•	Use APIs to facilitate Integration between Cisco DNA Center, Wireless LAN Controllers.

The Results:
•	Lower cost of wireless deployments
•	Increased accuracy and visibility

Business Summary
Simplify the Access Point deployments with an automation tool based on the Cisco DNA Center REST APIs.

