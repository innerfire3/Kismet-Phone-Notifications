import requests
from requests.auth import HTTPBasicAuth
import time
# by InnerFire3
# Get notification on your phone when a flipper device is near at your kismet device.
# Kismet server details
KISMET_URL = 'http://localhost:2501'
KISMET_API_DEVICES = '/devices/last-time/-{}/devices.json'
DEVICE_CHECK_INTERVAL = 10  # seconds
NOTIFICATION_INTERVAL = 300  # seconds (5 minutes)

# Authentication credentials
USERNAME = '<Your-Kismet-User-Here>'
PASSWORD = '<Your_Kismet_Password_Here>'

# Your Target server to notify app
TARGET_SERVER_URL = 'http://<your-ip-here>:6325/alerts'

# Prefix to check for
BLE_MAC_PREFIX = '80:E1:26'

# Dictionary to track the last notification time for each device
last_notification_time = {}
# Dictionary to track the last known state of each device
device_states = {}

# Function to get BLE devices from Kismet
def get_ble_devices(seconds):
    url = KISMET_URL + KISMET_API_DEVICES.format(seconds)
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch data from Kismet API, Status code: {response.status_code}")
        return []

# Function to check if a device is a BLE device and matches the prefix
def is_target_ble_device(device):
    mac_address = device.get('kismet.device.base.macaddr')
    if mac_address and mac_address.lower().startswith(BLE_MAC_PREFIX.lower()):
        return True
    return False

# Function to send notification to the target server
def notify_server(device):
    mac_address = device.get('kismet.device.base.macaddr')
    flipper_name = device.get('kismet.device.base.name', 'Unknown')
    message = f"Flipper found {flipper_name} with MAC {mac_address}"
    payload = {'message': message}

    try:
        response = requests.post(TARGET_SERVER_URL, data=payload)
        if response.status_code == 200:
            print(f"Notification sent successfully for device: {mac_address}")
        else:
            print(f"Failed to send notification, Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending notification: {e}")

# Main loop to monitor BLE devices
def main():
    while True:
        devices = get_ble_devices(DEVICE_CHECK_INTERVAL)
        current_devices = set()

        for device in devices:
            if is_target_ble_device(device):
                mac_address = device.get('kismet.device.base.macaddr')
                current_devices.add(mac_address)
                
                if mac_address not in device_states or device_states[mac_address] == "lost":
                    notify_server(device)
                    device_states[mac_address] = "found"

        # Update the state of devices not currently detected
        for mac_address in list(device_states.keys()):
            if mac_address not in current_devices:
                device_states[mac_address] = "lost"
                
        time.sleep(DEVICE_CHECK_INTERVAL)

if __name__ == "__main__":
    main()
