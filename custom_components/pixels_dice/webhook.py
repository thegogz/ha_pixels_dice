"""Webhook support for Pixels Dice integration."""
from __future__ import annotations

import json
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
    """Handle incoming webhook requests from Pixels Dice.

    Args:
        hass: The Home Assistant instance.
        webhook_id: The registered webhook identifier.
        request: The incoming HTTP request.

    Returns:
        An HTTP response indicating success or failure.
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
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

    # Validate numeric types
    if not isinstance(face_value, (int, float)):
        _LOGGER.warning("faceValue must be numeric, got %s", type(face_value).__name__)
        return web.Response(text="faceValue must be numeric", status=400)
    if not isinstance(led_count, (int, float)):
        _LOGGER.warning("ledCount must be numeric, got %s", type(led_count).__name__)
        return web.Response(text="ledCount must be numeric", status=400)
    if not isinstance(battery_level, (int, float)):
        _LOGGER.warning(
            "batteryLevel must be numeric, got %s", type(battery_level).__name__
        )
        return web.Response(text="batteryLevel must be numeric", status=400)

    # Get the first config entry (we only support one instance)
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        _LOGGER.error("No config entry found")
        return web.Response(text="Integration not configured", status=500)

    entry = entries[0]
    entity_id_prefix = f"{DOMAIN}_{pixel_id}"

    # Guard access to hass.data
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if entry_data is None:
        _LOGGER.error("Integration data not initialized for entry %s", entry.entry_id)
        return web.Response(text="Internal error", status=500)

    # Check if entity already exists
    registry = er.async_get(hass)
    entity_entries = er.async_entries_for_config_entry(registry, entry.entry_id)

    existing_entity = None
    for entity_entry in entity_entries:
        if entity_entry.unique_id == entity_id_prefix:
            entities = entry_data.get("entities", {})
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
            pixel_id,
            pixel_name,
            led_count,
            die_type,
            colorway,
            battery_level,
            initial_value=face_value,
        )

        entry_data.setdefault("entities", {})[pixel_id] = new_entity

        # Add entity using the callback stored during setup
        add_entities = entry_data.get("add_entities")
        if add_entities:
            add_entities([new_entity])
        else:
            _LOGGER.error("add_entities callback not found")
            return web.Response(text="Internal error", status=500)

    return web.Response(text="Success", status=200)


async def async_setup_webhook(hass: HomeAssistant, entry_id: str) -> None:
    """Set up the webhook for a config entry.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID to associate with the webhook.
    """
    webhook_id = DOMAIN

    if webhook_id not in hass.data.get("webhook", {}):
        async_register_webhook(
            hass, DOMAIN, "Pixels Dice", webhook_id, async_handle_webhook
        )
        _LOGGER.info("Registered webhook at: /api/webhook/%s", webhook_id)


async def async_unload_webhook(hass: HomeAssistant, entry_id: str) -> None:
    """Unload the webhook for a config entry.

    Args:
        hass: The Home Assistant instance.
        entry_id: The config entry ID being unloaded.
    """
    entries = hass.config_entries.async_entries(DOMAIN)
    if len(entries) <= 1:
        webhook_id = DOMAIN
        async_unregister_webhook(hass, webhook_id)
        _LOGGER.info("Unregistered webhook with ID: %s", webhook_id)
