"""The PulseGuard integration."""
import asyncio
import logging
from datetime import timedelta
import time
import json
import hashlib

import async_timeout
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_API_TOKEN,
    CONF_DEVICE_UUID,
    CONF_API_URL,
    DEFAULT_API_URL,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the PulseGuard component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up PulseGuard from a config entry."""
    
    # Get entry config data
    api_token = entry.data.get(CONF_API_TOKEN)
    device_uuid = entry.data.get(CONF_DEVICE_UUID)
    api_url = entry.data.get(CONF_API_URL, DEFAULT_API_URL)
    
    # Set up coordinator for data updates
    coordinator = PulseGuardCoordinator(
        hass,
        _LOGGER,
        api_token=api_token,
        device_uuid=device_uuid,
        api_url=api_url,
    )
    
    # Initial data update
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator for this entry
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Set up all platforms for this device
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
    return unload_ok

class PulseGuardCoordinator(DataUpdateCoordinator):
    """Data update coordinator for PulseGuard."""
    
    def __init__(self, hass, logger, api_token, device_uuid, api_url):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )
        
        self.api_token = api_token
        self.device_uuid = device_uuid
        self.api_url = api_url
        self.start_time = time.time()
        self.last_data_hash = None
        self.error_count = 0
        
    async def _async_update_data(self):
        """Fetch data from PulseGuard API."""
        try:
            async with async_timeout.timeout(10):
                # Get system stats
                system_stats = await self.hass.async_add_executor_job(
                    self._get_system_stats
                )
                
                # Reset error count on successful update
                if self.error_count > 0:
                    self.error_count = 0
                    _LOGGER.info("Successfully reconnected to PulseGuard API after %d errors", self.error_count)
                
                # Return all collected data
                return {
                    "system": system_stats,
                }
        except Exception as err:
            self.error_count += 1
            # Only log every 5 errors to avoid flooding the logs
            if self.error_count == 1 or self.error_count % 5 == 0:
                _LOGGER.error("Error #%d communicating with PulseGuard API: %s", self.error_count, err)
            raise UpdateFailed(f"Error communicating with API: {err}")
    
    def _get_system_stats(self):
        """Get system statistics."""
        import requests
        import psutil
        
        # Get system metrics similar to what the Linux agent collects
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # Get uptime - safely handle missing uptime sensor
        try:
            if "uptime" in self.hass.data and hasattr(self.hass.data["uptime"], "value"):
                uptime_seconds = int(self.hass.data["uptime"].value())
            else:
                # Calculate uptime from when this integration started
                uptime_seconds = int(time.time() - self.start_time)
        except Exception:
            # Fallback to runtime since component started
            uptime_seconds = int(time.time() - self.start_time)
        
        # Get system information
        import platform
        hostname = platform.node()
        ip_address = self._get_local_ip()
        mac_address = self._get_mac_address()
        os_type = "homeassistant"
        os_version = platform.version()
        
        # Create system specs payload
        system_specs = {
            "cpu_cores": psutil.cpu_count(logical=True),
            "total_memory": memory.total // (1024 * 1024)  # Convert to MB
        }
        
        # Create metrics payload
        metrics = {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage,
            "uptime": uptime_seconds
        }
        
        # Calculate a hash of the data to check if it has changed
        data_to_hash = f"{cpu_usage}-{memory_usage}-{disk_usage}-{uptime_seconds}"
        current_hash = hashlib.md5(data_to_hash.encode()).hexdigest()
        
        # Create the full data payload
        data = {
            "hostname": hostname,
            "ip_address": ip_address,
            "mac_address": mac_address,
            "os_type": os_type,
            "os_version": os_version,
            "system_specs": system_specs,
            "metrics": metrics,
            "services": []
        }
        
        # Send check-in to PulseGuard API
        check_in_url = f"{self.api_url}/devices/check-in"
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Token": self.api_token,
            "Accept": "application/json"
        }
        
        try:
            # Only log the data if it has changed significantly or it's the first time
            if self.last_data_hash is None or self.last_data_hash != current_hash:
                _LOGGER.debug("Sending check-in to PulseGuard API with data: %s", json.dumps(data))
                self.last_data_hash = current_hash
            
            response = requests.post(check_in_url, headers=headers, json=data, timeout=10)
            
            # Log response only if it's an error
            if response.status_code >= 400:
                _LOGGER.error("Error response from PulseGuard API: %s - %s", 
                             response.status_code, response.text)
            response.raise_for_status()
            
            # Return the metrics as they'll be needed for the sensors
            return metrics
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error sending check-in to PulseGuard API: %s", err)
            # Include response details if available
            if hasattr(err, "response") and err.response is not None:
                _LOGGER.error("Response content: %s", err.response.text)
            return metrics
    
    def _get_local_ip(self):
        """Get the local IP address."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except Exception:
            return "127.0.0.1"
    
    def _get_mac_address(self):
        """Get the MAC address."""
        import uuid
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                            for elements in range(0, 8 * 6, 8)][::-1])
            return mac
        except Exception:
            return "00:00:00:00:00:00" 