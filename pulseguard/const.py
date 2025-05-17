"""Constants for the PulseGuard integration."""

DOMAIN = "pulseguard"

# Configuration fields
CONF_DEVICE_ID = "device_id"
CONF_API_URL = "api_url"
CONF_REPORT_INTERVAL = "report_interval"
CONF_INCLUDE_SENSORS = "include_sensors"
CONF_MONITOR_ADDONS = "monitor_addons"

# Defaults
DEFAULT_API_URL = "https://app.pulseguard.nl/api"
DEFAULT_REPORT_INTERVAL = 60
DEFAULT_INCLUDE_SENSORS = True
DEFAULT_MONITOR_ADDONS = True 