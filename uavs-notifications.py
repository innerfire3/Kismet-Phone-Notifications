import time
import requests
import json
from requests.auth import HTTPBasicAuth
import re
# by InnerFire3
# Get notification on your phone when a UAVs wifi device is near at your kismet device.
# Configuration
matcher_url = "http://localhost:2501/phy/phyuav/manuf_matchers.json"
ssid_url = "http://localhost:2501/phy/phy80211/ssids/views/ssids.json"

# Your Target server to notify app
notification_url = "http://<your-ip-here>:6325/alerts"

check_interval = 150  # 2.5 minutes in seconds

username = "<Your-Kismet-User-Here>"  # Replace with your username
password = "<Your_Kismet_Password_Here>"  # Replace with your password

notified_ssids = set()

# Function to fetch matchers
def fetch_matchers():
    try:
        response = requests.get(matcher_url, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred while fetching matchers: {req_err}")
        return []

# Function to fetch SSIDs
def fetch_ssids():
    try:
        response = requests.get(ssid_url, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred while fetching SSIDs: {req_err}")
        return []

# Function to check for matching SSIDs
def check_for_matches(matchers, ssids):
    global notified_ssids
    for ssid in ssids:
        ssid_name = ssid.get("dot11.ssidgroup.ssid", "")
        if ssid_name in notified_ssids:
            continue
        for matcher in matchers:
            ssid_regex = matcher.get("uav.manufmatch.ssid_regex", "")
            if re.match(ssid_regex, ssid_name):
                notification_message = f"UAV detected: {matcher.get('uav_match_name', 'Unknown')} - {ssid_name}"
                send_notification(notification_message)
                notified_ssids.add(ssid_name)
                break

# Function to send notification
def send_notification(message):
    try:
        response = requests.post(notification_url, data=message.encode('utf-8'))
        response.raise_for_status()
        print("Notification sent successfully.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")

# Main loop
if __name__ == "__main__":
    matchers = fetch_matchers()
    if matchers:
        while True:
            ssids = fetch_ssids()
            if ssids:
                check_for_matches(matchers, ssids)
            time.sleep(check_interval)
