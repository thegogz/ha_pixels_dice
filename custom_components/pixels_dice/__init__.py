from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .webhook import async_setup_webhook

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Pixels Dice integration."""
    hass.data[DOMAIN] = {}
    await async_setup_webhook(hass)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Pixels Dice from a config entry."""
    hass.data[DOMAIN][entry.entry_id] = {}
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
