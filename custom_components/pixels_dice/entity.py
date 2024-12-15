from homeassistant.helpers.entity import Entity

class PixelsDiceEntity(Entity):
    def __init__(self, pixel_id, pixel_name, led_count, die_type, colorway, battery_level):
        """Initialize the Pixel Dice entity."""
        self._pixel_id = pixel_id
        self._pixel_name = pixel_name
        self._led_count = led_count
        self._die_type = die_type
        self._colorway = colorway
        self._battery_level = battery_level
        self._state = None

    @property
    def unique_id(self):
        return str(self._pixel_id)

    @property
    def name(self):
        return self._pixel_name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            "led_count": self._led_count,
            "die_type": self._die_type,
            "colorway": self._colorway,
            "battery_level": self._battery_level,
        }

    def update_state(self, face_value, die_type, colorway, battery_level):
        """Update the entity's state and attributes."""
        self._state = face_value
        self._die_type = die_type
        self._colorway = colorway
        self._battery_level = battery_level
        self.schedule_update_ha_state()
