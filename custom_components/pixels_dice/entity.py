"""Entity for Pixels Dice integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


class PixelsDiceEntity(SensorEntity):
    """Representation of a Pixels Dice sensor."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        pixel_id: int,
        pixel_name: str,
        led_count: int,
        die_type: str,
        colorway: str,
        battery_level: float,
    ) -> None:
        """Initialize the Pixel Dice entity."""
        self._pixel_id = pixel_id
        self._pixel_name = pixel_name
        self._led_count = led_count
        self._die_type = die_type
        self._colorway = colorway
        self._battery_level = battery_level
        self._attr_native_value = None
        self._attr_unique_id = f"{DOMAIN}_{pixel_id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Pixels Dice."""
        # Include die_type in the device name for clarity
        device_name = f"{self._die_type.upper()} - {self._pixel_name}"
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._pixel_id))},
            name=device_name,
            manufacturer="Pixels",
            model=self._die_type,
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return "Roll Value"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "led_count": self._led_count,
            "die_type": self._die_type,
            "colorway": self._colorway,
            "battery_level": self._battery_level,
        }

    def update_state(
        self, face_value: int, die_type: str, colorway: str, battery_level: float
    ) -> None:
        """Update the entity's state and attributes."""
        self._attr_native_value = face_value
        self._die_type = die_type
        self._colorway = colorway
        self._battery_level = battery_level
        self.async_write_ha_state()
