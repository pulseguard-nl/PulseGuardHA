# PulseGuard for Home Assistant

PulseGuard integration for Home Assistant allows you to monitor your Home Assistant instance and track system performance metrics from your PulseGuard dashboard.

## Features

- Monitor CPU, memory, and disk usage
- Automatic check-ins and status reporting
- Customizable reporting interval
- Track add-on status (optional)

## Installation

### HACS Installation (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Go to HACS → Integrations → "+" → "Custom Repository"
3. Enter repository URL: `https://github.com/pulseguard/home-assistant-integration`
4. Select "Integration" as the category
5. Click "Add"
6. Find and install "PulseGuard" from the list of integrations

### Manual Installation

1. Download the latest release from GitHub
2. Copy the `pulseguard` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

### UI Configuration (Recommended)

The easiest way to set up PulseGuard is through the Home Assistant UI:

1. Go to Settings → Devices & Services
2. Click the "+ ADD INTEGRATION" button
3. Search for "PulseGuard" and select it
4. Enter your PulseGuard API token and Device ID
5. Click "Submit" to complete the setup

### YAML Configuration (Alternative)

Alternatively, you can configure PulseGuard by adding this to your `configuration.yaml` file:

```yaml
pulseguard:
  api_token: "YOUR_API_TOKEN"
  device_id: "YOUR_DEVICE_ID"
  report_interval: 60  # Optional: Reporting interval in seconds (default: 60)
```

### Configuration Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `api_token` | string | Yes | - | Your PulseGuard API token |
| `device_id` | string | Yes | - | Your PulseGuard device ID |
| `api_url` | string | No | `https://app.pulseguard.nl/api` | PulseGuard API URL |
| `report_interval` | integer | No | 60 | Reporting interval in seconds |
| `include_sensors` | boolean | No | true | Include Home Assistant sensor data |
| `monitor_addons` | boolean | No | true | Monitor Home Assistant add-ons |

## Troubleshooting

If you're having issues with the integration, check the Home Assistant logs for error messages related to PulseGuard.

1. Check that your API token and device ID are correct
2. Ensure your Home Assistant instance has internet access
3. Check the logs for any error messages

## Support

For support, please visit [PulseGuard Support](https://pulseguard.nl/support) or open an issue on our [GitHub repository](https://github.com/pulseguard/home-assistant-integration/issues). 