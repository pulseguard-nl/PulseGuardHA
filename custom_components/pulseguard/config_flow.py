"""Config flow for PulseGuard integration."""
from __future__ import annotations

import logging
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
        
        # Try to call the API to validate the credentials
        api_url = data.get(CONF_API_URL, DEFAULT_API_URL)
        device_uuid = data[CONF_DEVICE_UUID]
        api_token = data[CONF_API_TOKEN]
        
        # Test API connectivity
        response = await hass.async_add_executor_job(
            lambda: requests.post(
                f"{api_url}/devices/check-in",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Token": api_token,
                    "Accept": "application/json",
                },
                json={
                    "test": True,
                    "hostname": "Home Assistant Integration Test",
                },
                timeout=10,
            )
        )
        
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