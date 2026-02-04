"""Entity for Pixels Dice integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


class PixelsDiceEntity(SensorEntity):
    """Representation of a Pixels Dice sensor.

    Each physical die is represented as a single sensor entity whose state
    is the most recent roll value.
    """

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
        initial_value: int | None = None,
    ) -> None:
        """Initialize the Pixel Dice entity.

        Args:
            pixel_id: Unique hardware identifier of the die.
            pixel_name: User-assigned name of the die.
            led_count: Number of LEDs on the die (correlates with face count).
            die_type: Die type string (e.g. "d20", "d6").
            colorway: Colorway identifier of the die.
            battery_level: Battery charge level as a float 0.0–1.0.
            initial_value: Optional initial roll value to set before the
                entity is added to Home Assistant.
        """
        self._pixel_id = pixel_id
        self._pixel_name = pixel_name
        self._led_count = led_count
        self._die_type = die_type
        self._colorway = colorway
        self._battery_level = battery_level
        self._attr_native_value = initial_value
        self._attr_unique_id = f"{DOMAIN}_{pixel_id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Pixels Dice.

        Returns:
            DeviceInfo identifying the physical die as a device.
        """
        device_name = f"{self._die_type.upper()} - {self._pixel_name}"
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._pixel_id))},
            name=device_name,
            manufacturer="Pixels",
            model=self._die_type,
        )

    @property
    def name(self) -> str:
        """Return the name of the entity.

        Returns:
            The entity name displayed in the UI.
        """
        return "Roll Value"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes.

        Returns:
            Dictionary of additional die attributes exposed to HA.
        """
        return {
            "led_count": self._led_count,
            "die_type": self._die_type,
            "colorway": self._colorway,
            "battery_level": self._battery_level,
        }

    def update_state(
        self, face_value: int, die_type: str, colorway: str, battery_level: float
    ) -> None:
        """Update the entity's state and attributes.

        Args:
            face_value: The new roll value.
            die_type: Updated die type string.
            colorway: Updated colorway identifier.
            battery_level: Updated battery level.
        """
        self._attr_native_value = face_value
        self._die_type = die_type
        self._colorway = colorway
        self._battery_level = battery_level
        self.async_write_ha_state()
