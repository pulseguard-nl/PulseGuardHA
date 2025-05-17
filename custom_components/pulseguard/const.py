"""Constants for the PulseGuard integration."""

DOMAIN = "pulseguard"

# Config entry keys
CONF_API_TOKEN = "api_token"
CONF_DEVICE_UUID = "device_uuid"
CONF_API_URL = "api_url"

# Default values
DEFAULT_API_URL = "https://app.pulseguard.nl/api"

# Entity attributes
ATTR_CPU_USAGE = "cpu_usage"
ATTR_MEMORY_USAGE = "memory_usage"
ATTR_DISK_USAGE = "disk_usage"
ATTR_UPTIME = "uptime"

# Platform types
PLATFORMS = ["sensor"]

# Sensor types
SENSOR_TYPE_CPU = "cpu"
SENSOR_TYPE_MEMORY = "memory"
SENSOR_TYPE_DISK = "disk"
SENSOR_TYPE_UPTIME = "uptime"
SENSOR_TYPE_STATUS = "status"

# Sensor names
SENSOR_NAME_CPU = "CPU Usage"
SENSOR_NAME_MEMORY = "Memory Usage"
SENSOR_NAME_DISK = "Disk Usage"
SENSOR_NAME_UPTIME = "Uptime"
SENSOR_NAME_STATUS = "Status"

# Sensor units
SENSOR_UNIT_PERCENTAGE = "%"
SENSOR_UNIT_TIME = "s" 