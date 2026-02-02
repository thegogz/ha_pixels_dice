"""Webhook support for Pixels Dice integration."""
from __future__ import annotations

import logging

from aiohttp import web
from homeassistant.components.webhook import (
    async_register as async_register_webhook,
    async_unregister as async_unregister_webhook,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN
from .entity import PixelsDiceEntity

_LOGGER = logging.getLogger(__name__)


async def async_handle_webhook(
    hass: HomeAssistant, webhook_id: str, request: web.Request
) -> web.Response:
    """Handle incoming webhook requests from Pixels Dice."""
    try:
        data = await request.json()
    except ValueError:
        _LOGGER.warning("Received webhook with invalid JSON")
        return web.Response(text="Invalid JSON", status=400)

    # Validate required fields
    if "pixelId" not in data:
        _LOGGER.warning("Received webhook missing pixelId")
        return web.Response(text="Missing pixelId", status=400)

    pixel_id = data.get("pixelId")
    pixel_name = data.get("pixelName", "Unknown Dice")
    face_value = data.get("faceValue")
    led_count = data.get("ledCount")
    die_type = data.get("dieType", "d20")
    colorway = data.get("colorway", "default")
    battery_level = data.get("batteryLevel", 0.0)

    if face_value is None or led_count is None:
        _LOGGER.warning("Received webhook missing critical data (faceValue or ledCount)")
        return web.Response(text="Missing critical data", status=400)

    # Get the first config entry (we only support one instance)
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        _LOGGER.error("No config entry found for Pixels Dice")
        return web.Response(text="Integration not configured", status=500)

    entry = entries[0]
    entity_id_prefix = f"{DOMAIN}_{pixel_id}"

    # Check if entity already exists
    registry = er.async_get(hass)
    entity_entries = er.async_entries_for_config_entry(registry, entry.entry_id)

    existing_entity = None
    for entity_entry in entity_entries:
        if entity_entry.unique_id == entity_id_prefix:
            # Found existing entity, get it from hass.data
            entities = hass.data[DOMAIN].get(entry.entry_id, {}).get("entities", {})
            existing_entity = entities.get(pixel_id)
            break

    if existing_entity:
        # Update existing entity
        _LOGGER.debug("Updating existing dice %s with roll value %s", pixel_id, face_value)
        existing_entity.update_state(face_value, die_type, colorway, battery_level)
    else:
        # Create new entity
        _LOGGER.info("Creating new dice entity for pixel_id %s", pixel_id)
        new_entity = PixelsDiceEntity(
            pixel_id, pixel_name, led_count, die_type, colorway, battery_level
        )
        # Set initial state (don't write to HA yet - entity not added)
        new_entity._attr_native_value = face_value

        # Store entity and add it
        if "entities" not in hass.data[DOMAIN][entry.entry_id]:
            hass.data[DOMAIN][entry.entry_id]["entities"] = {}

        hass.data[DOMAIN][entry.entry_id]["entities"][pixel_id] = new_entity

        # Add entity using the callback stored during setup
        add_entities = hass.data[DOMAIN][entry.entry_id].get("add_entities")
        if add_entities:
            add_entities([new_entity])
        else:
            _LOGGER.error("add_entities callback not found")
            return web.Response(text="Internal error", status=500)

    return web.Response(text="Success", status=200)


async def async_setup_webhook(hass: HomeAssistant, entry_id: str) -> None:
    """Set up the webhook for a config entry."""
    # Use a fixed webhook ID so users always know the URL
    webhook_id = DOMAIN

    # Only register if not already registered (handles multiple config entries)
    if webhook_id not in hass.data.get("webhook", {}):
        async_register_webhook(
            hass, DOMAIN, "Pixels Dice", webhook_id, async_handle_webhook
        )
        _LOGGER.info("Registered webhook at: /api/webhook/%s", webhook_id)


async def async_unload_webhook(hass: HomeAssistant, entry_id: str) -> None:
    """Unload the webhook for a config entry."""
    # Only unregister if this is the last config entry
    entries = hass.config_entries.async_entries(DOMAIN)
    if len(entries) <= 1:
        webhook_id = DOMAIN
        async_unregister_webhook(hass, webhook_id)
        _LOGGER.info("Unregistered webhook with ID: %s", webhook_id)
