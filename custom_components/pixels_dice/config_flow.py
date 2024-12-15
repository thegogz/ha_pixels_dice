from homeassistant import config_entries
from .const import DOMAIN

class PixelsDiceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pixels Dice."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        return self.async_create_entry(title="Pixels Dice", data={})
