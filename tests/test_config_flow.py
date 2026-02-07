"""Tests for the Pixels Dice config flow."""
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.pixels_dice.const import DOMAIN, CONF_WEBHOOK_ID, DEFAULT_WEBHOOK_ID


async def test_user_flow_shows_form(hass: HomeAssistant) -> None:
    """Test that the initial step shows a form with webhook_id field."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert CONF_WEBHOOK_ID in result["data_schema"].schema


async def test_user_flow_shows_confirm_step(hass: HomeAssistant) -> None:
    """Test that submitting user step shows confirmation with webhook URL."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "confirm"
    assert "webhook_url" in result["description_placeholders"]
    assert DEFAULT_WEBHOOK_ID in result["description_placeholders"]["webhook_url"]


async def test_user_flow_creates_entry_with_default_webhook(hass: HomeAssistant) -> None:
    """Test that completing the flow creates an entry with default webhook ID."""
    # Step 1: User form
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )

    # Step 2: Confirm
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Pixels Dice"
    assert result["data"] == {CONF_WEBHOOK_ID: DEFAULT_WEBHOOK_ID}


async def test_user_flow_creates_entry_with_custom_webhook(hass: HomeAssistant) -> None:
    """Test that a custom webhook ID is saved in the config entry."""
    custom_id = "my_custom_dice_webhook"

    # Step 1: User form with custom webhook ID
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_WEBHOOK_ID: custom_id}
    )

    # Confirm step should show custom webhook URL
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "confirm"
    assert custom_id in result["description_placeholders"]["webhook_url"]

    # Step 2: Confirm
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_WEBHOOK_ID: custom_id}


async def test_user_flow_aborts_if_already_configured(hass: HomeAssistant) -> None:
    """Test that a second flow aborts when already configured."""
    # Create a first entry (complete both steps)
    first = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    first = await hass.config_entries.flow.async_configure(
        first["flow_id"], user_input={}
    )
    await hass.config_entries.flow.async_configure(
        first["flow_id"], user_input={}
    )

    # Second flow should abort
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
