"""The Pixels Dice integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_WEBHOOK_ID, DEFAULT_WEBHOOK_ID
from .webhook import async_setup_webhook, async_unload_webhook

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pixels Dice from a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being set up.

    Returns:
        True if setup was successful.
    """
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    # Get webhook ID from config (with fallback for existing entries)
    webhook_id = entry.data.get(CONF_WEBHOOK_ID, DEFAULT_WEBHOOK_ID)

    # Set up webhook for this config entry
    await async_setup_webhook(hass, entry.entry_id, webhook_id)

    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("Integration setup complete for entry %s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being unloaded.

    Returns:
        True if unload was successful.
    """
    # Get webhook ID from config (with fallback for existing entries)
    webhook_id = entry.data.get(CONF_WEBHOOK_ID, DEFAULT_WEBHOOK_ID)

    # Unload webhook
    await async_unload_webhook(hass, entry.entry_id, webhook_id)

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
