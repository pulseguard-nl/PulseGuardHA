"""Support for PulseGuard sensors."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from . import PulseGuardCoordinator
from .const import (
    ATTR_CPU_USAGE,
    ATTR_DISK_USAGE,
    ATTR_MEMORY_USAGE,
    ATTR_UPTIME,
    DOMAIN,
    SENSOR_NAME_CPU,
    SENSOR_NAME_DISK,
    SENSOR_NAME_MEMORY,
    SENSOR_NAME_UPTIME,
    SENSOR_TYPE_CPU,
    SENSOR_TYPE_DISK,
    SENSOR_TYPE_MEMORY,
    SENSOR_TYPE_UPTIME,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the PulseGuard sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create a unique ID for the device
    device_uuid = entry.data.get("device_uuid", entry.entry_id)
    
    # Create sensors for all monitored metrics
    sensors = [
        PulseGuardCpuSensor(coordinator, device_uuid),
        PulseGuardMemorySensor(coordinator, device_uuid),
        PulseGuardDiskSensor(coordinator, device_uuid),
        PulseGuardUptimeSensor(coordinator, device_uuid),
    ]
    
    async_add_entities(sensors)


class PulseGuardSensor(CoordinatorEntity, SensorEntity):
    """Base class for all PulseGuard sensors."""

    _attr_has_entity_name = True
    
    def __init__(
        self,
        coordinator: PulseGuardCoordinator,
        device_uuid: str,
        sensor_type: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self._device_uuid = device_uuid
        self._sensor_type = sensor_type
        
        # Set up device info and entity attributes
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_uuid)},
            name=f"PulseGuard Monitor",
            manufacturer="PulseGuard",
            model="Home Assistant Integration",
            sw_version="1.0.0",
        )
        
        # Entity attributes
        self._attr_unique_id = f"{device_uuid}_{sensor_type}"
        self._attr_name = name
        self._attr_state_class = SensorStateClass.MEASUREMENT
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class PulseGuardCpuSensor(PulseGuardSensor):
    """Sensor for CPU usage."""

    def __init__(self, coordinator: PulseGuardCoordinator, device_uuid: str) -> None:
        """Initialize the CPU sensor."""
        super().__init__(
            coordinator, device_uuid, SENSOR_TYPE_CPU, SENSOR_NAME_CPU
        )
        self._attr_icon = "mdi:cpu-64-bit"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_class = SensorDeviceClass.POWER_FACTOR
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        # Get CPU usage from coordinator data
        return round(self.coordinator.data.get("system", {}).get(ATTR_CPU_USAGE, 0), 1)


class PulseGuardMemorySensor(PulseGuardSensor):
    """Sensor for memory usage."""

    def __init__(self, coordinator: PulseGuardCoordinator, device_uuid: str) -> None:
        """Initialize the memory sensor."""
        super().__init__(
            coordinator, device_uuid, SENSOR_TYPE_MEMORY, SENSOR_NAME_MEMORY
        )
        self._attr_icon = "mdi:memory"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_class = SensorDeviceClass.POWER_FACTOR
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        # Get memory usage from coordinator data
        return round(self.coordinator.data.get("system", {}).get(ATTR_MEMORY_USAGE, 0), 1)


class PulseGuardDiskSensor(PulseGuardSensor):
    """Sensor for disk usage."""

    def __init__(self, coordinator: PulseGuardCoordinator, device_uuid: str) -> None:
        """Initialize the disk sensor."""
        super().__init__(
            coordinator, device_uuid, SENSOR_TYPE_DISK, SENSOR_NAME_DISK
        )
        self._attr_icon = "mdi:harddisk"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_class = SensorDeviceClass.POWER_FACTOR
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        # Get disk usage from coordinator data
        return round(self.coordinator.data.get("system", {}).get(ATTR_DISK_USAGE, 0), 1)


class PulseGuardUptimeSensor(PulseGuardSensor):
    """Sensor for system uptime."""

    def __init__(self, coordinator: PulseGuardCoordinator, device_uuid: str) -> None:
        """Initialize the uptime sensor."""
        super().__init__(
            coordinator, device_uuid, SENSOR_TYPE_UPTIME, SENSOR_NAME_UPTIME
        )
        self._attr_icon = "mdi:clock-outline"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_native_unit_of_measurement = "s"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        # Get uptime from coordinator data
        return self.coordinator.data.get("system", {}).get(ATTR_UPTIME, 0)
    
    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
        
        uptime_seconds = self.coordinator.data.get("system", {}).get(ATTR_UPTIME, 0)
        
        # Convert to human-readable format
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_human = ""
        if days > 0:
            uptime_human += f"{int(days)} days, "
        if hours > 0 or days > 0:
            uptime_human += f"{int(hours)} hours, "
        if minutes > 0 or hours > 0 or days > 0:
            uptime_human += f"{int(minutes)} minutes"
        else:
            uptime_human += f"{int(seconds)} seconds"
        
        return {
            "human_readable": uptime_human,
        } 