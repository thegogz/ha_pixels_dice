"""Config flow for Pixels Dice integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.network import get_url

from .const import DOMAIN, CONF_WEBHOOK_ID, DEFAULT_WEBHOOK_ID

VERSION = 1


class PixelsDiceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pixels Dice."""

    VERSION = VERSION

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._webhook_id: str = DEFAULT_WEBHOOK_ID

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step where user can customize webhook ID.

        Args:
            user_input: User-submitted form data, or None on first display.

        Returns:
            A ConfigFlowResult that shows the form or proceeds to confirmation.
        """
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            self._webhook_id = user_input.get(CONF_WEBHOOK_ID, DEFAULT_WEBHOOK_ID)
            return await self.async_step_confirm()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_WEBHOOK_ID, default=DEFAULT_WEBHOOK_ID): str,
                }
            ),
        )

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show confirmation step with webhook URL and instructions.

        Args:
            user_input: User-submitted form data, or None on first display.

        Returns:
            A ConfigFlowResult that shows instructions or creates the entry.
        """
        if user_input is not None:
            return self.async_create_entry(
                title="Pixels Dice",
                data={CONF_WEBHOOK_ID: self._webhook_id},
            )

        # Try to get the HA base URL for display
        try:
            base_url = get_url(self.hass, prefer_external=False)
        except Exception:  # noqa: BLE001
            base_url = "http://<your-home-assistant-url>"

        webhook_url = f"{base_url}/api/webhook/{self._webhook_id}"

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "webhook_url": webhook_url,
                "webhook_id": self._webhook_id,
            },
        )
