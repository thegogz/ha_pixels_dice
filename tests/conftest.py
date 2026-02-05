"""Shared fixtures for Pixels Dice tests."""
import pytest

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
async def hass_with_http(hass: HomeAssistant):
    """Set up hass with HTTP and webhook components for webhook testing.

    Handles proper cleanup to avoid thread leakage.
    """
    await async_setup_component(hass, "http", {})
    await async_setup_component(hass, "webhook", {})
    yield hass
    # Stop HTTP server to clean up threads
    if hass.http is not None:
        await hass.http.stop()


@pytest.fixture
def sample_webhook_payload() -> dict:
    """Return a full valid webhook payload."""
    return {
        "pixelId": 12345678,
        "pixelName": "Test D20",
        "faceValue": 20,
        "ledCount": 20,
        "dieType": "d20",
        "colorway": "onyxBlack",
        "batteryLevel": 0.85,
    }


@pytest.fixture
def minimal_webhook_payload() -> dict:
    """Return a payload with only the required fields."""
    return {
        "pixelId": 99999999,
        "faceValue": 6,
        "ledCount": 6,
    }
