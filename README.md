# PulseGuard for Home Assistant

This is the Home Assistant integration for PulseGuard monitoring system. Monitor your Home Assistant instance with the same powerful tools used for monitoring Linux and Windows devices.

## Features

- Monitor CPU, memory, and disk usage of your Home Assistant instance
- Track system uptime
- Send metrics to your PulseGuard dashboard
- Get alerts when your Home Assistant instance exceeds thresholds or goes offline

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS → Integrations → Add Integration
3. Search for "PulseGuard" and install it
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/pulseguard` directory to your Home Assistant `/config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. After installation, go to Home Assistant → Settings → Devices & Services
2. Click on "+ Add Integration" button
3. Search for "PulseGuard" and select it
4. Enter your PulseGuard Device UUID and API Token (these can be found in your PulseGuard dashboard)
5. Click Submit

## Requirements

- You must have a PulseGuard account
- You need to create a device in your PulseGuard dashboard to get a Device UUID and API Token

## Troubleshooting

- If the integration fails to connect, check your Device UUID and API Token
- Ensure your Home Assistant instance can reach the PulseGuard API server
- Check the Home Assistant logs for any error messages

## Getting Help

If you need help with this integration:

1. Check the [PulseGuard documentation](https://www.pulseguard.nl/docs)
2. Report issues on our [GitHub repository](https://github.com/pulseguard/home-assistant-integration)
3. Contact our support team at support@pulseguard.nl

## License

This integration is released under the MIT License. 