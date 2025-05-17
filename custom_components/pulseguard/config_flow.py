"""Config flow for PulseGuard integration."""
from __future__ import annotations

import logging
import json
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_API_TOKEN,
    CONF_DEVICE_UUID,
    CONF_API_URL,
    DEFAULT_API_URL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Data schema for the user input
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_UUID): str,
        vol.Required(CONF_API_TOKEN): str,
        vol.Optional(CONF_API_URL, default=DEFAULT_API_URL): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Validate the API token and device UUID by making a test API call
    try:
        import requests
        import platform
        import socket
        import uuid
        import psutil
        
        # Try to call the API to validate the credentials
        api_url = data.get(CONF_API_URL, DEFAULT_API_URL)
        device_uuid = data[CONF_DEVICE_UUID]
        api_token = data[CONF_API_TOKEN]
        
        # Get system info for validation request
        hostname = platform.node()
        
        # Get IP address
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
        except Exception:
            ip_address = "127.0.0.1"
            
        # Get MAC address
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                            for elements in range(0, 8 * 6, 8)][::-1])
        except Exception:
            mac = "00:00:00:00:00:00"
        
        # Get system metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # Create validation data with all required fields
        validation_data = {
            "hostname": f"Home Assistant - {hostname}",
            "ip_address": ip_address,
            "mac_address": mac,
            "os_type": "homeassistant",
            "os_version": platform.version(),
            "system_specs": {
                "cpu_cores": psutil.cpu_count(logical=True),
                "total_memory": memory.total // (1024 * 1024)  # Convert to MB
            },
            "metrics": {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "disk_usage": disk_usage,
                "uptime": 60  # Just a placeholder for validation
            },
            "services": []
        }
        
        # Log the actual data being sent
        _LOGGER.debug("Sending validation data to PulseGuard API: %s", json.dumps(validation_data))
        
        # Test API connectivity
        response = await hass.async_add_executor_job(
            lambda: requests.post(
                f"{api_url}/devices/check-in",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Token": api_token,
                    "Accept": "application/json",
                },
                json=validation_data,
                timeout=10,
            )
        )
        
        # Log response details
        _LOGGER.debug("API Response Status: %s", response.status_code)
        _LOGGER.debug("API Response Body: %s", response.text[:200])  # First 200 chars to avoid massive logs
        
        # If the server responds with an error, raise an exception
        response.raise_for_status()
        
        # Return validated data
        return {
            CONF_DEVICE_UUID: device_uuid,
            CONF_API_TOKEN: api_token,
            CONF_API_URL: api_url,
        }
    except requests.exceptions.RequestException as err:
        _LOGGER.error("Error connecting to PulseGuard API: %s", err)
        if hasattr(err, "response") and err.response is not None:
            _LOGGER.error("Response content: %s", err.response.text)
        raise CannotConnect from err
    except Exception as err:
        _LOGGER.exception("Unexpected error: %s", err)
        raise CannotValidate from err


class PulseGuardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PulseGuard."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                # Validate the API token and device UUID
                validated_input = await validate_input(self.hass, user_input)
                
                # Create a unique ID for the config entry
                device_uuid = validated_input[CONF_DEVICE_UUID]
                
                # Check if this device is already configured
                await self.async_set_unique_id(device_uuid)
                self._abort_if_unique_id_configured()
                
                # Create the config entry
                return self.async_create_entry(
                    title=f"PulseGuard Monitor",
                    data=validated_input,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except CannotValidate:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        
        # Show the form to the user
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class CannotValidate(HomeAssistantError):
    """Error to indicate we cannot validate the input.""" 