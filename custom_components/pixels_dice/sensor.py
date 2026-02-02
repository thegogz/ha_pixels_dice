"""Sensor platform for Pixels Dice integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up Pixels Dice sensors from a config entry."""
    # Store the add_entities callback in hass.data so webhook can use it
    hass.data[DOMAIN][entry.entry_id]["add_entities"] = async_add_entities

    _LOGGER.info("Pixels Dice sensor platform setup complete")
    return True
