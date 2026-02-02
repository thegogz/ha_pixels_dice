"""Config flow for Pixels Dice integration."""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

VERSION = 1


class PixelsDiceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pixels Dice."""

    VERSION = VERSION

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Only allow a single instance of this integration
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            # Create the config entry
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title="Pixels Dice", data={})

        # Show the user a form to confirm setup
        return self.async_show_form(step_id="user")
