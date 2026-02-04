"""Config flow for Pixels Dice integration."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN

VERSION = 1


class PixelsDiceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pixels Dice."""

    VERSION = VERSION

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step.

        Args:
            user_input: User-submitted form data, or None on first display.

        Returns:
            A ConfigFlowResult that either shows the form, creates an entry,
            or aborts if already configured.
        """
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="Pixels Dice", data={})

        return self.async_show_form(step_id="user")
