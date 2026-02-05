"""Tests for the Pixels Dice webhook handler."""
from homeassistant.core import HomeAssistant

from custom_components.pixels_dice.const import DOMAIN

from pytest_homeassistant_custom_component.common import MockConfigEntry


WEBHOOK_URL = "/api/webhook/pixels_dice"


async def _setup_integration(hass: HomeAssistant) -> MockConfigEntry:
    """Set up the Pixels Dice integration and return the config entry.

    Args:
        hass: The Home Assistant instance (must have HTTP already set up).

    Returns:
        The created MockConfigEntry.
    """
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_webhook_valid_payload(
    hass_with_http: HomeAssistant, hass_client_no_auth, sample_webhook_payload: dict
) -> None:
    """Test a valid webhook creates an entity and returns 200."""
    entry = await _setup_integration(hass_with_http)
    client = await hass_client_no_auth()

    response = await client.post(WEBHOOK_URL, json=sample_webhook_payload)

    assert response.status == 200

    # Verify entity was stored
    entities = hass_with_http.data[DOMAIN][entry.entry_id].get("entities", {})
    assert sample_webhook_payload["pixelId"] in entities
    entity = entities[sample_webhook_payload["pixelId"]]
    assert entity._attr_native_value == sample_webhook_payload["faceValue"]


async def test_webhook_update_existing_entity(
    hass_with_http: HomeAssistant, hass_client_no_auth, sample_webhook_payload: dict
) -> None:
    """Test that a second webhook for the same pixelId updates the entity."""
    entry = await _setup_integration(hass_with_http)
    client = await hass_client_no_auth()

    # First request creates the entity
    response1 = await client.post(WEBHOOK_URL, json=sample_webhook_payload)
    assert response1.status == 200

    # Second request updates it
    updated_payload = {**sample_webhook_payload, "faceValue": 1}
    response2 = await client.post(WEBHOOK_URL, json=updated_payload)
    assert response2.status == 200

    entities = hass_with_http.data[DOMAIN][entry.entry_id]["entities"]
    entity = entities[sample_webhook_payload["pixelId"]]
    assert entity._attr_native_value == 1


async def test_webhook_invalid_json(
    hass_with_http: HomeAssistant, hass_client_no_auth
) -> None:
    """Test that invalid JSON returns 400."""
    await _setup_integration(hass_with_http)
    client = await hass_client_no_auth()

    response = await client.post(
        WEBHOOK_URL, data=b"not json at all", headers={"Content-Type": "application/json"}
    )

    assert response.status == 400
    text = await response.text()
    assert "Invalid JSON" in text


async def test_webhook_missing_pixel_id(
    hass_with_http: HomeAssistant, hass_client_no_auth
) -> None:
    """Test that a payload missing pixelId returns 400."""
    await _setup_integration(hass_with_http)
    client = await hass_client_no_auth()

    response = await client.post(WEBHOOK_URL, json={"faceValue": 20, "ledCount": 20})

    assert response.status == 400
    text = await response.text()
    assert "Missing pixelId" in text


async def test_webhook_missing_critical_fields(
    hass_with_http: HomeAssistant, hass_client_no_auth
) -> None:
    """Test that missing faceValue or ledCount returns 400."""
    await _setup_integration(hass_with_http)
    client = await hass_client_no_auth()

    # Missing faceValue
    response1 = await client.post(WEBHOOK_URL, json={"pixelId": 111, "ledCount": 20})
    assert response1.status == 400

    # Missing ledCount
    response2 = await client.post(WEBHOOK_URL, json={"pixelId": 222, "faceValue": 20})
    assert response2.status == 400


async def test_webhook_invalid_numeric_data(
    hass_with_http: HomeAssistant, hass_client_no_auth
) -> None:
    """Test that non-numeric faceValue, ledCount, or batteryLevel returns 400."""
    await _setup_integration(hass_with_http)
    client = await hass_client_no_auth()

    # String faceValue
    response = await client.post(WEBHOOK_URL, json={
        "pixelId": 333,
        "faceValue": "twenty",
        "ledCount": 20,
    })
    assert response.status == 400
    text = await response.text()
    assert "faceValue" in text

    # String ledCount
    response = await client.post(WEBHOOK_URL, json={
        "pixelId": 333,
        "faceValue": 20,
        "ledCount": "twenty",
    })
    assert response.status == 400
    text = await response.text()
    assert "ledCount" in text

    # String batteryLevel
    response = await client.post(WEBHOOK_URL, json={
        "pixelId": 333,
        "faceValue": 20,
        "ledCount": 20,
        "batteryLevel": "full",
    })
    assert response.status == 400
    text = await response.text()
    assert "batteryLevel" in text


async def test_webhook_defaults_applied(
    hass_with_http: HomeAssistant, hass_client_no_auth, minimal_webhook_payload: dict
) -> None:
    """Test that optional fields get default values."""
    entry = await _setup_integration(hass_with_http)
    client = await hass_client_no_auth()

    response = await client.post(WEBHOOK_URL, json=minimal_webhook_payload)
    assert response.status == 200

    pixel_id = minimal_webhook_payload["pixelId"]
    entities = hass_with_http.data[DOMAIN][entry.entry_id]["entities"]
    entity = entities[pixel_id]

    attrs = entity.extra_state_attributes
    assert attrs["die_type"] == "d20"
    assert attrs["colorway"] == "default"
    assert attrs["battery_level"] == 0.0
