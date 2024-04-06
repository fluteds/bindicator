import time
import threading
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
import requests
import os
import config  # Importing the configuration file
import logging
import json
from icalendar import Calendar

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to scrape bin collection data from iCalendar file or website if URL is specified
def scrape_bin_data():
    if config.CALENDAR_URL:
        # Use calendar URL if specified
        response = requests.get(config.CALENDAR_URL)
        cal = Calendar.from_ical(response.text)
    else:
        # Use local calendar file if no URL is specified
        with open(os.path.join(os.path.dirname(__file__), config.CALENDAR_FILE_NAME), 'rb') as f:
            cal = Calendar.from_ical(f.read())

    # Find events relevant to bin collection
    bin_events = []
    for event in cal.walk('vevent'):
        if 'Recycling' in event.get('summary') or 'Rubbish' in event.get('summary'):
            bin_events.append(event)

    # Sort events by date
    bin_events.sort(key=lambda x: x.get('dtstart').dt)

    # Get the next bin collection event
    next_bin_event = bin_events[0] if bin_events else None

    # Extract relevant information
    if next_bin_event:
        # Construct a list of summaries for events on the same day
        bin_summaries = [event.get('summary') for event in bin_events if event.get('dtstart').dt.date() == next_bin_event.get('dtstart').dt.date()]
        combined_summary = ", ".join(bin_summaries)
        logging.info(f"Next bin collection event: {combined_summary}")

        bin_data = {
            'summary': combined_summary,
            'start_time': next_bin_event.get('dtstart').dt,
            'end_time': next_bin_event.get('dtend').dt if 'dtend' in next_bin_event else None
        }

        return bin_data
    else:
        return None

def control_pc_lights(bin_data):
    # Initialize OpenRGBClient with specified options
    client = OpenRGBClient(config.OPENRGB_SERVER_IP, config.OPENRGB_SERVER_PORT, config.OPENRGB_CLIENT_NAME)

    # Get all devices
    devices = client.devices
    for device in devices:
        logging.info(f"Device {device.name} found")

        # Set profile based on bin data
        profile_index = 0  # Default to the first profile in the list
        if "Recycling" in bin_data['summary'] and "Rubbish" in bin_data['summary']:
            profile_name = config.RECYCLING_RUBBISH_PROFILE_NAME
        elif "Recycling" in bin_data['summary']:
            profile_name = config.RECYCLING_PROFILE_NAME
        elif "Rubbish" in bin_data['summary']:
            profile_name = config.RUBBISH_PROFILE_NAME
        else:
            logging.error("Unknown bin collection event type")

        # Find the index of the profile by name
        for index, profile in enumerate(client.profiles):
            if profile_name in profile.name:
                profile_index = index
                break

        # Load the profile by index
        client.load_profile(profile_index)
        logging.info(f"Loaded profile: {profile_name}")

# Function to send push notification via Bark
def send_push_notification(bin_data):
    # Extracting bin types from the combined summary
    bin_types = []
    if "Recycling" in bin_data['summary']:
        bin_types.append("Recycling")
    if "Rubbish" in bin_data['summary']:
        bin_types.append("Rubbish")

    # Compose the message with the bin types and reminder
    if len(bin_types) == 1:
        message = f"Next bin collection: {bin_types[0]}. Remember to put the bin out by 7am."
    elif len(bin_types) > 1:
        message = f"Next bin collections: {bin_types[0]} and {bin_types[1]}. Remember to put the bins out by 7am."

    # Send the push notification using Bark API
    try:
        notification_data = {
            "title": "Bins",
            "body": message,
            "sound": "",
            "url": "",
            "level": "timeSensitive",
            "group": "Bin Collection Reminders",
            "automaticallyCopy": "1"
        }

        response = requests.post(
            url=f"https://api.day.app/{config.BARK_API_KEY}",
            headers={"Content-Type": "application/json; charset=utf-8"},
            data=json.dumps(notification_data)
        )

        if response.status_code == 200:
            logging.info("Push notification sent successfully.")
        else:
            logging.error(f"Failed to send push notification. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Notification failed to send. Error: {e}")

def main():
    # Scrape bin data
    bin_data = scrape_bin_data()
    if bin_data:
        # Control PC lights based on bin data
        control_pc_lights(bin_data)
        
        # Check if notification key is provided
        if config.BARK_API_KEY:
            # Send push notification
            send_push_notification(bin_data)
        else:
            logging.warning("Notification key not provided in config. Skipping push notification.")
    else:
        logging.warning("No upcoming bin collection events found.")

if __name__ == "__main__":
    main()
