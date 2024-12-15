from homeassistant.core import HomeAssistant
from homeassistant.components.webhook import async_register as async_register_webhook
from .entity import PixelsDiceEntity
from .const import DOMAIN

async def async_handle_webhook(hass: HomeAssistant, webhook_id: str, request):
    """Handle the webhook request."""
    data = await request.json()
    if 'pixelId' not in data:
        return "Missing pixelId in the webhook request", 400
    
    pixel_id = data.get('pixelId')
    pixel_name = data.get('pixelName', 'Unknown Dice')
    face_value = data.get('faceValue', None)
    led_count = data.get('ledCount', None)
    die_type = data.get('dieType', 'd20')
    colorway = data.get('colorway', 'default')
    battery_level = data.get('batteryLevel', 0.0)

    if not all([pixel_id, face_value, led_count]):
        return "Missing critical data", 400

    # Try to retrieve or create the entity
    entity = hass.data[DOMAIN].get(pixel_id)
    if not entity:
        entity = PixelsDiceEntity(pixel_id, pixel_name, led_count, die_type, colorway, battery_level)
        hass.data[DOMAIN][pixel_id] = entity
        hass.async_create_task(hass.helpers.entity_component.async_add_entities([entity]))

    # Update the entity state
    entity.update_state(face_value, die_type, colorway, battery_level)
    return "Success", 200

async def async_setup_webhook(hass: HomeAssistant):
    """Set up the webhook for Pixels Dice."""
    webhook_id = "pixels_dice"
    async_register_webhook(hass, webhook_id, async_handle_webhook)
