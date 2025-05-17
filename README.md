# PulseGuard for Home Assistant

This is the Home Assistant integration for the PulseGuard monitoring system. Monitor your Home Assistant instance with the same powerful tools used for monitoring Linux and Windows devices.

## Features

* Monitor CPU, memory, and disk usage of your Home Assistant instance
* Track system uptime
* Send metrics to your PulseGuard dashboard
* Get alerts when your Home Assistant instance exceeds thresholds or goes offline

## Requirements

* You must have a PulseGuard account (sign up at [https://app.pulseguard.nl](https://app.pulseguard.nl) if you don't have one)
* You need to create a device in your PulseGuard dashboard to get a Device UUID and API Token

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS → Integrations → Three dots in top right → Custom repositories
3. Add `https://github.com/pulseguard-nl/PulseGuardHA` as a custom repository (Category: Integration)
4. Click "Add"
5. Search for "PulseGuard" in the Integrations tab and install it
6. Restart Home Assistant

### Manual Installation

1. Download the latest release from this repository
2. Extract the contents
3. Copy the `custom_components/pulseguard` directory to your Home Assistant `/config/custom_components/` directory
4. Restart Home Assistant

## Configuration

1. In your PulseGuard dashboard, create a new device:
   - Go to Devices → Add Device
   - Give it a name (e.g., "Home Assistant")
   - Select "Other" as the device type
   - Copy the generated Device UUID and API Token

2. After installation, go to Home Assistant → Settings → Devices & Services
3. Click on "+ Add Integration" button
4. Search for "PulseGuard" and select it
5. Enter your PulseGuard Device UUID and API Token (from step 1)
6. Click Submit

## How It Works

Once configured, the integration will:

1. Collect system metrics (CPU, memory, disk usage, uptime) from your Home Assistant instance
2. Send these metrics to your PulseGuard dashboard at regular intervals
3. Allow you to monitor your Home Assistant instance alongside other devices
4. Send alerts based on your configured thresholds in PulseGuard

## Troubleshooting

### Connection Issues

If the integration fails to connect, try these steps:

1. Verify your Device UUID and API Token are correct
2. Ensure your Home Assistant instance can reach the PulseGuard API server (default: `https://app.pulseguard.nl/api`)
3. Check the Home Assistant logs for specific error messages

### Testing API Connectivity

This repository includes a standalone test script that can help identify API connectivity issues:

1. Copy the `test_api.py` script to your system
2. Run it with your device credentials:
   ```
   python test_api.py <device_uuid> <api_token>
   ```
3. The script will show detailed information about the API request and response

### Common Errors

- **422 Unprocessable Content**: This usually means there's an issue with the format of the data being sent. Check the logs for details.
- **401 Unauthorized**: Your API Token is incorrect or has expired.
- **Connection Error**: Your Home Assistant instance cannot reach the PulseGuard API server.

## Getting Help

If you need help with this integration:

1. Check the [PulseGuard documentation](https://pulseguard.nl/docs)
2. Report issues on our [GitHub repository](https://github.com/pulseguard-nl/PulseGuardHA/issues)
3. Contact our support team at support@pulseguard.nl

## License

This integration is released under the MIT License. 