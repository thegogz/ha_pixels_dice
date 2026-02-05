"""Tests for the Pixels Dice webhook handler."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant

from custom_components.pixels_dice.const import DOMAIN
from custom_components.pixels_dice.webhook import async_handle_webhook

from pytest_homeassistant_custom_component.common import MockConfigEntry


def _make_mock_request(payload: dict | None = None, raw_data: bytes | None = None):
    """Create a mock aiohttp request with the given payload.

    Args:
        payload: Dict to be returned by request.json().
        raw_data: Raw bytes that will cause JSONDecodeError if not valid JSON.

    Returns:
        A mock request object.
    """
    request = MagicMock()
    if raw_data is not None:
        request.json = AsyncMock(side_effect=json.JSONDecodeError("", "", 0))
    elif payload is not None:
        request.json = AsyncMock(return_value=payload)
    else:
        request.json = AsyncMock(return_value={})
    return request


async def _setup_integration(hass: HomeAssistant) -> MockConfigEntry:
    """Set up the Pixels Dice integration and return the config entry.

    Args:
        hass: The Home Assistant instance.

    Returns:
        The created MockConfigEntry.
    """
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_webhook_valid_payload(
    hass: HomeAssistant, sample_webhook_payload: dict
) -> None:
    """Test a valid webhook creates an entity and returns 200."""
    entry = await _setup_integration(hass)
    request = _make_mock_request(sample_webhook_payload)

    response = await async_handle_webhook(hass, DOMAIN, request)

    assert response.status == 200

    # Verify entity was stored
    entities = hass.data[DOMAIN][entry.entry_id].get("entities", {})
    assert sample_webhook_payload["pixelId"] in entities
    entity = entities[sample_webhook_payload["pixelId"]]
    assert entity._attr_native_value == sample_webhook_payload["faceValue"]


async def test_webhook_update_existing_entity(
    hass: HomeAssistant, sample_webhook_payload: dict
) -> None:
    """Test that a second webhook for the same pixelId updates the entity."""
    entry = await _setup_integration(hass)

    # First request creates the entity
    request1 = _make_mock_request(sample_webhook_payload)
    response1 = await async_handle_webhook(hass, DOMAIN, request1)
    assert response1.status == 200

    # Second request updates it
    updated_payload = {**sample_webhook_payload, "faceValue": 1}
    request2 = _make_mock_request(updated_payload)
    response2 = await async_handle_webhook(hass, DOMAIN, request2)
    assert response2.status == 200

    entities = hass.data[DOMAIN][entry.entry_id]["entities"]
    entity = entities[sample_webhook_payload["pixelId"]]
    assert entity._attr_native_value == 1


async def test_webhook_invalid_json(hass: HomeAssistant) -> None:
    """Test that invalid JSON returns 400."""
    await _setup_integration(hass)
    request = _make_mock_request(raw_data=b"not json at all")

    response = await async_handle_webhook(hass, DOMAIN, request)

    assert response.status == 400
    assert "Invalid JSON" in response.text


async def test_webhook_missing_pixel_id(hass: HomeAssistant) -> None:
    """Test that a payload missing pixelId returns 400."""
    await _setup_integration(hass)
    request = _make_mock_request({"faceValue": 20, "ledCount": 20})

    response = await async_handle_webhook(hass, DOMAIN, request)

    assert response.status == 400
    assert "Missing pixelId" in response.text


async def test_webhook_missing_critical_fields(hass: HomeAssistant) -> None:
    """Test that missing faceValue or ledCount returns 400."""
    await _setup_integration(hass)

    # Missing faceValue
    request1 = _make_mock_request({"pixelId": 111, "ledCount": 20})
    response1 = await async_handle_webhook(hass, DOMAIN, request1)
    assert response1.status == 400

    # Missing ledCount
    request2 = _make_mock_request({"pixelId": 222, "faceValue": 20})
    response2 = await async_handle_webhook(hass, DOMAIN, request2)
    assert response2.status == 400


async def test_webhook_invalid_numeric_data(hass: HomeAssistant) -> None:
    """Test that non-numeric faceValue, ledCount, or batteryLevel returns 400."""
    await _setup_integration(hass)

    # String faceValue
    request = _make_mock_request({
        "pixelId": 333,
        "faceValue": "twenty",
        "ledCount": 20,
    })
    response = await async_handle_webhook(hass, DOMAIN, request)
    assert response.status == 400
    assert "faceValue" in response.text

    # String ledCount
    request = _make_mock_request({
        "pixelId": 333,
        "faceValue": 20,
        "ledCount": "twenty",
    })
    response = await async_handle_webhook(hass, DOMAIN, request)
    assert response.status == 400
    assert "ledCount" in response.text

    # String batteryLevel
    request = _make_mock_request({
        "pixelId": 333,
        "faceValue": 20,
        "ledCount": 20,
        "batteryLevel": "full",
    })
    response = await async_handle_webhook(hass, DOMAIN, request)
    assert response.status == 400
    assert "batteryLevel" in response.text


async def test_webhook_defaults_applied(
    hass: HomeAssistant, minimal_webhook_payload: dict
) -> None:
    """Test that optional fields get default values."""
    entry = await _setup_integration(hass)
    request = _make_mock_request(minimal_webhook_payload)

    response = await async_handle_webhook(hass, DOMAIN, request)
    assert response.status == 200

    pixel_id = minimal_webhook_payload["pixelId"]
    entities = hass.data[DOMAIN][entry.entry_id]["entities"]
    entity = entities[pixel_id]

    attrs = entity.extra_state_attributes
    assert attrs["die_type"] == "d20"
    assert attrs["colorway"] == "default"
    assert attrs["battery_level"] == 0.0
