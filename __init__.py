"""
PulseGuard Home Assistant Integration.

For more information about this integration, see:
https://app.pulseguard.nl/
"""
import asyncio
import logging
import json
import platform
import socket
import time
from datetime import datetime, timedelta

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_TOKEN, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_DEVICE_ID,
    CONF_API_URL,
    CONF_REPORT_INTERVAL,
    CONF_INCLUDE_SENSORS,
    CONF_MONITOR_ADDONS,
    DEFAULT_API_URL,
    DEFAULT_REPORT_INTERVAL,
    DEFAULT_INCLUDE_SENSORS,
    DEFAULT_MONITOR_ADDONS,
)

_LOGGER = logging.getLogger(__name__)

# Support for YAML configuration (legacy method)
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_TOKEN): cv.string,
                vol.Required(CONF_DEVICE_ID): cv.string,
                vol.Optional(CONF_API_URL, default=DEFAULT_API_URL): cv.url,
                vol.Optional(CONF_REPORT_INTERVAL, default=DEFAULT_REPORT_INTERVAL): cv.positive_int,
                vol.Optional(CONF_INCLUDE_SENSORS, default=DEFAULT_INCLUDE_SENSORS): cv.boolean,
                vol.Optional(CONF_MONITOR_ADDONS, default=DEFAULT_MONITOR_ADDONS): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the PulseGuard component from YAML configuration."""
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN not in config:
        return True

    # If we have a YAML config but also config entries, don't process the YAML config
    if hass.config_entries.async_entries(DOMAIN):
        return True

    # Create a config entry from the YAML configuration
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "import"}, data=config[DOMAIN]
        )
    )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PulseGuard from a config entry."""
    api_token = entry.data[CONF_API_TOKEN]
    device_id = entry.data[CONF_DEVICE_ID]
    api_url = entry.data.get(CONF_API_URL, DEFAULT_API_URL)
    
    # Get options with fallback to defaults
    report_interval = entry.options.get(
        CONF_REPORT_INTERVAL, 
        entry.data.get(CONF_REPORT_INTERVAL, DEFAULT_REPORT_INTERVAL)
    )
    include_sensors = entry.options.get(
        CONF_INCLUDE_SENSORS, 
        entry.data.get(CONF_INCLUDE_SENSORS, DEFAULT_INCLUDE_SENSORS)
    )
    monitor_addons = entry.options.get(
        CONF_MONITOR_ADDONS, 
        entry.data.get(CONF_MONITOR_ADDONS, DEFAULT_MONITOR_ADDONS)
    )
    
    pulseguard = PulseGuardApi(hass, api_token, device_id, api_url)
    
    # Create update coordinator
    coordinator = PulseGuardDataUpdateCoordinator(
        hass,
        _LOGGER,
        pulseguard=pulseguard,
        name="pulseguard",
        update_interval=timedelta(seconds=report_interval),
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator and API in hass.data
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": pulseguard,
    }
    
    # Set up update listener for config changes
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    # Register services if needed
    # hass.services.async_register(...)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)
        
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

class PulseGuardDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching PulseGuard data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        pulseguard,
        name: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=update_interval,
        )
        self.pulseguard = pulseguard

    async def _async_update_data(self):
        """Update data via API."""
        try:
            response = await self.pulseguard.check_in()
            return response
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
    
class PulseGuardApi:
    """API client for PulseGuard."""
    
    def __init__(self, hass, api_token, device_id, api_url):
        """Initialize the API client."""
        self.hass = hass
        self.api_token = api_token
        self.device_id = device_id
        self.api_url = api_url
        self.device_info = self._get_device_info()
        self.session = async_get_clientsession(hass)
        
    def _get_device_info(self):
        """Get information about the Home Assistant instance."""
        return {
            "hostname": socket.gethostname(),
            "ip_address": self._get_local_ip(),
            "os_type": "homeassistant",
            "os_version": self.hass.config.version,
            "mac_address": self._get_mac_address(),
        }
    
    def _get_local_ip(self):
        """Get the local IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
            
    def _get_mac_address(self):
        """Get the MAC address."""
        try:
            from uuid import getnode
            mac = ':'.join(['{:02x}'.format((getnode() >> elements) & 0xff) 
                for elements in range(0, 8*6, 8)][::-1])
            return mac
        except Exception:
            return "00:00:00:00:00:00"
    
    async def check_in(self):
        """Send metrics to PulseGuard API."""
        metrics = await self._get_system_metrics()
        
        payload = {
            **self.device_info,
            "metrics": metrics,
            "system_specs": self._get_system_specs(),
            "services": await self._get_running_services(),
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Token": self.api_token,
            "Accept": "application/json",
        }
        
        check_in_url = f"{self.api_url}/devices/check-in"
        
        try:
            async with self.session.post(
                check_in_url, 
                headers=headers, 
                json=payload, 
                timeout=10
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    _LOGGER.debug("PulseGuard check-in successful: %s", response_data)
                    return response_data
                else:
                    _LOGGER.error(
                        "PulseGuard check-in failed with status %s: %s", 
                        response.status, 
                        await response.text()
                    )
                    return None
        except aiohttp.ClientError as ex:
            _LOGGER.error("Error connecting to PulseGuard API: %s", ex)
            return None
            
    async def _get_system_metrics(self):
        """Get system metrics."""
        import psutil
        
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_usage": cpu_usage,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "uptime_seconds": int(time.time() - self.hass.start_time.timestamp()),
        }
    
    def _get_system_specs(self):
        """Get system specifications."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            return {
                "cpu_cores": psutil.cpu_count(logical=True),
                "total_memory": memory.total // (1024 * 1024),  # MB
                "platform": platform.platform(),
                "ha_version": self.hass.config.version,
            }
        except Exception as ex:
            _LOGGER.error("Error collecting system specs: %s", ex)
            return {}
    
    async def _get_running_services(self):
        """Get running services in Home Assistant."""
        try:
            services = []
            
            # Include core services
            services.append("Home Assistant Core")
            
            # Check if we can access the Supervisor API
            has_supervisor = False
            try:
                has_supervisor = self.hass.components.hassio is not None
            except (AttributeError, ModuleNotFoundError):
                pass

            # If Supervisor is available, list add-ons
            if has_supervisor:
                try:
                    supervisor = await self.hass.components.hassio.async_get_info()
                    if supervisor:
                        services.append(f"Supervisor {supervisor.get('supervisor', 'unknown')}")
                        
                    # List running add-ons if available
                    try:
                        addons = await self.hass.components.hassio.async_get_addon_info("core_ssh")
                        if addons and addons.get('state') == 'started':
                            services.append(f"Add-on: {addons.get('name', 'SSH')}")
                    except Exception:
                        pass
                except Exception as ex:
                    _LOGGER.debug("Error getting supervisor info: %s", ex)
                
            return services
        except Exception as ex:
            _LOGGER.error("Error collecting services: %s", ex)
            return [] 