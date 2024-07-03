import time
import requests
import json
from requests.auth import HTTPBasicAuth
# by InnerFire3
# Get all notifications from Kismet on your phone using notify app
# Configuration
alert_url = "http://localhost:2501/alerts/all_alerts.json"

# Your Target server to notify app
notification_url = "http://<your-ip-here>:6325/alerts"

check_interval = 300  # 5 minutes in seconds
username = "<Your-Kismet-User-Here>"  # Replace with your username
password = "<Your_Kismet_Password_Here>"  # Replace with your password

last_alert_timestamp = 0

# Function to check for new notifications
def check_for_alerts():
    global last_alert_timestamp
    try:
        print("Fetching alerts...")
        response = requests.get(alert_url, auth=HTTPBasicAuth(username, password))
        print(f"HTTP Status Code: {response.status_code}")
        response.raise_for_status()
        alerts = response.json()

        if alerts:  # If there are any alerts
            for alert in alerts:
                alert_timestamp = alert.get("kismet.alert.timestamp", 0)
                # Check if the alert is newer than the last alert timestamp
                if alert_timestamp > last_alert_timestamp:
                    last_alert_timestamp = alert_timestamp
                    notification_message = alert.get("kismet.alert.text", "No message available")
                    send_notification(notification_message)
                    break  # Exit loop after sending the first new notification
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")

# Function to send notification
def send_notification(message):
    try:
        response = requests.post(notification_url, data=message)
        response.raise_for_status()
        print("Notification sent successfully.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")

# Main loop
if __name__ == "__main__":
    while True:
        check_for_alerts()
        time.sleep(check_interval)
