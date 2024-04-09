# Bindicator

Reminds you of upcoming bin collection events by changing your RGB lighting to the respective bin colours that need to go out and sending a push notification straight to your mobile. Inspired by [this X post](https://nitter.poast.org/tarbard/status/1002464120447397888) and [YouTube video here.](https://invidious.poast.org/watch?v=YSBioki_03g)

## Installation

1. Install the required dependencies.
2. Setup and start your OpenRGB server.
3. Configure the script by editing and renaming the `example.config.py` file to `config.py`.
4. Run the script.

## Configuration

The script needs to be setup by modifying the `config.py` file. Here are the configurable parameters:

- `CALENDAR_URL`: URL to the iCalendar file.
- `CALENDAR_FILE_NAME`: Name of the local ICS file.
- `OPENRGB_SERVER_IP`: IP address of the OpenRGB server.
- `OPENRGB_SERVER_PORT`: Port of the OpenRGB server.
- `OPENRGB_CLIENT_NAME`: Name of the OpenRGB client. (Optional)
- `RECYCLING_PROFILE_NAME`: Name of your recycling profile name. (Required)
- `RUBBISH_PROFILE_NAME`: Name of your rubbish profile name. (Required)
- `RECYCLING_RUBBISH_PROFILE_NAME`: Name of profile when both bins are going out. (Required)
- `BARK_API_KEY`: Device key for the Bark push notification service. (Optional)

>[!NOTE]
> OpenRBG profiles created with external plugins do not work. If you have a plugin profile that is on using an external plugin (e.g Effects plugin) the script will not override the plugin profile, meaning the bins profile is set and loaded but not shown until the plugin profile is unloaded. This is to do with the OpenRBG-Python library and I haven't worked out a way to get around this.
