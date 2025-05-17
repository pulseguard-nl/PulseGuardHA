"""Config flow for PulseGuard integration."""
import logging
import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_API_TOKEN

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

class PulseGuardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PulseGuard."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate API Token and Device ID by trying to connect to a test endpoint (if available)
            # or by simply storing them. For this example, we'll assume they are valid.
            # You should implement actual validation against your API.
            session = async_get_clientsession(self.hass)
            api_url = user_input.get(CONF_API_URL, DEFAULT_API_URL)
            api_token = user_input[CONF_API_TOKEN]
            device_id = user_input[CONF_DEVICE_ID]

            # Minimal validation: check if API token and device ID are provided
            if not api_token:
                errors["base"] = "invalid_auth"
                errors[CONF_API_TOKEN] = "API Token is required."
            if not device_id:
                errors["base"] = "invalid_auth"
                errors[CONF_DEVICE_ID] = "Device ID is required."

            if not errors:
                try:
                    # Example: Test connection (replace with actual API call)
                    # test_url = f"{api_url.rstrip('/')}/test_connection"
                    # headers = {"Authorization": f"Bearer {api_token}", "X-Device-ID": device_id}
                    # async with session.get(test_url, headers=headers, timeout=10) as response:
                    #     if response.status != 200:
                    #         _LOGGER.error(f"Connection test failed: {response.status}")
                    #         errors["base"] = "cannot_connect"
                    #     else:
                    #         _LOGGER.info("Successfully connected to PulseGuard API for config flow.")
                    
                    # For now, we assume connection is successful if fields are filled
                    # You can create a unique ID for the config entry if needed, e.g., based on device_id
                    await self.async_set_unique_id(device_id)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(title=f"PulseGuard ({device_id})", data=user_input)

                except aiohttp.ClientError:
                    _LOGGER.error("Error connecting to PulseGuard API during config flow")
                    errors["base"] = "cannot_connect"
                except Exception as e:  # pylint: disable=broad-except
                    _LOGGER.exception(f"Unexpected exception in config flow: {e}")
                    errors["base"] = "unknown"
        
        # Default values for the form
        data_schema = vol.Schema({
            vol.Required(CONF_API_TOKEN): str,
            vol.Required(CONF_DEVICE_ID): str,
            vol.Optional(CONF_API_URL, default=DEFAULT_API_URL): str,
            vol.Optional(CONF_REPORT_INTERVAL, default=DEFAULT_REPORT_INTERVAL): cv.positive_int,
            vol.Optional(CONF_INCLUDE_SENSORS, default=DEFAULT_INCLUDE_SENSORS): bool,
            vol.Optional(CONF_MONITOR_ADDONS, default=DEFAULT_MONITOR_ADDONS): bool,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow for this handler."""
        return PulseGuardOptionsFlowHandler(config_entry)


class PulseGuardOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for PulseGuard."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Add validation for options if needed
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Optional(
                CONF_API_URL, 
                default=self.config_entry.options.get(CONF_API_URL, self.config_entry.data.get(CONF_API_URL, DEFAULT_API_URL))
            ): str,
            vol.Optional(
                CONF_REPORT_INTERVAL, 
                default=self.config_entry.options.get(CONF_REPORT_INTERVAL, self.config_entry.data.get(CONF_REPORT_INTERVAL, DEFAULT_REPORT_INTERVAL))
            ): cv.positive_int,
            vol.Optional(
                CONF_INCLUDE_SENSORS, 
                default=self.config_entry.options.get(CONF_INCLUDE_SENSORS, self.config_entry.data.get(CONF_INCLUDE_SENSORS, DEFAULT_INCLUDE_SENSORS))
            ): bool,
            vol.Optional(
                CONF_MONITOR_ADDONS, 
                default=self.config_entry.options.get(CONF_MONITOR_ADDONS, self.config_entry.data.get(CONF_MONITOR_ADDONS, DEFAULT_MONITOR_ADDONS))
            ): bool,
        })

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        ) 