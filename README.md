# Pixels Dice

A Home Assistant custom integration for tracking and managing Pixels smart dice.

## Features

- **Automatic Device Discovery**: Each Pixels die automatically creates its own device on first contact
- **Real-time Roll Tracking**: Tracks roll results (face_value) as the sensor state
- **Device Registry Integration**: Each die appears as a device with manufacturer, model, and attributes
- **Multi-Dice Support**: Supports unlimited dice (tested with up to 27 dice)
- **Customizable Naming**: Rename devices and entities through the Home Assistant UI
- **Additional Attributes**: die_type, colorway, battery_level, and led_count

## Installation

### Manual Installation

1. Copy the `pixels_dice` folder to your Home Assistant `custom_components` directory:

```
custom_components/
└── pixels_dice/
    ├── __init__.py
    ├── manifest.json
    ├── const.py
    ├── entity.py
    ├── sensor.py
    ├── config_flow.py
    ├── strings.json
    └── webhook.py
```

2. Restart Home Assistant.

3. Go to **Settings** → **Devices & Services** → **Integrations** and click **Add Integration**.

4. Search for "Pixels Dice" and follow the setup prompts.

## Webhook Configuration

The integration uses a **fixed webhook endpoint** to receive data from your Pixels dice.

### Setting Up Your Dice

Configure your Pixels dice to send data to this webhook URL:

```
/api/webhook/pixels_dice
```

**Full URL examples:**
- Local access: `http://homeassistant.local:8123/api/webhook/pixels_dice`
- IP address: `http://192.168.1.100:8123/api/webhook/pixels_dice`
- Nabu Casa: `https://your-instance.ui.nabu.casa/api/webhook/pixels_dice`
- Custom domain: `https://your-domain.com/api/webhook/pixels_dice`

> **Note**: The port (8123) is the default for local Home Assistant installations. If you're using SSL, Nabu Casa, or a reverse proxy, adjust the URL accordingly.

### Webhook Data Format

Your Pixels dice will automatically send roll data in the following JSON format:

```json
{
  "pixelId": 12345678,
  "pixelName": "Red Dragon",
  "faceValue": 20,
  "ledCount": 20,
  "dieType": "d20",
  "colorway": "onyxBlack",
  "batteryLevel": 0.85
}
```

#### Required Fields
The dice must send these fields:
- `pixelId` (integer): Unique identifier for the die
- `faceValue` (integer): Current roll result (1-20 for d20, 1-6 for d6, etc.)
- `ledCount` (integer): Number of LEDs on the die

#### Recommended Fields
For proper device naming and display:
- `pixelName` (string): Display name for the die (default: "Unknown Dice")
- `dieType` (string): Type of die - d4, d6, d8, d10, d12, d20, etc. (default: "d20")
  - **Important**: This is used in the device name, so it's recommended to set it correctly

#### Optional Fields
- `colorway` (string): Color scheme of the die (default: "default")
- `batteryLevel` (float): Battery level 0.0-1.0 (default: 0.0)

## How It Works

1. **Setup**: Add the integration through the Home Assistant UI
2. **First Contact**: When a die sends its first webhook, a new device and sensor entity are created
3. **Device Creation**: Each die becomes a device named `{DIE_TYPE} - {PIXEL_NAME}` (e.g., "D20 - Red Dragon")
4. **Entity Creation**: Each device has a "Roll Value" sensor showing the latest roll
5. **Updates**: Subsequent webhook calls update the sensor state and attributes

### Entity Naming

Entities are created with the pattern:
```
sensor.{die_type}_{pixel_name}_roll_value
```

Examples:
- `sensor.d20_red_dragon_roll_value`
- `sensor.d6_fireball_roll_value`
- `sensor.d12_ancient_one_roll_value`

The `unique_id` is based on `pixelId`, so you can safely rename devices and entities in the UI without breaking the integration.

## Entity Details

### Sensor State
The sensor state displays the most recent roll result (face_value).

### Attributes
Each sensor includes the following attributes:
- `led_count`: Number of LEDs on the die
- `die_type`: Type of die (d20, d6, etc.)
- `colorway`: Color scheme of the die
- `battery_level`: Current battery level (0.0 to 1.0)

### Device Information
Each die is registered as a device with:
- **Manufacturer**: Pixels
- **Model**: Die type (d20, d6, etc.)
- **Name**: `{DIE_TYPE} - {PIXEL_NAME}`
- **Identifiers**: Based on pixelId

## Testing

You can test the webhook using curl or any HTTP client:

```bash
curl -X POST http://homeassistant.local:8123/api/webhook/pixels_dice \
  -H "Content-Type: application/json" \
  -d '{
    "pixelId": 12345678,
    "pixelName": "Test D20",
    "faceValue": 20,
    "ledCount": 20,
    "dieType": "d20",
    "colorway": "onyxBlack",
    "batteryLevel": 0.85
  }'
```

> Replace `homeassistant.local:8123` with your actual Home Assistant URL and port.

**After sending the webhook:**
1. Go to **Developer Tools** → **States**
2. Look for `sensor.d20_test_d20_roll_value`
3. Verify the state is `20` and attributes contain the die information

## Troubleshooting

### Check Integration Logs

Look for these log messages in **Settings** → **System** → **Logs**:

```
INFO (MainThread) [custom_components.pixels_dice.webhook] Registered webhook at: /api/webhook/pixels_dice
INFO (MainThread) [custom_components.pixels_dice] Pixels Dice integration setup complete
INFO (MainThread) [custom_components.pixels_dice.webhook] Creating new dice entity for pixel_id 12345678
```

### Common Issues

1. **Webhook not receiving data**: Verify the URL and ensure your Home Assistant is accessible from the dice
2. **Entities not appearing**: Check logs for errors and verify the JSON format matches the required fields
3. **Integration not showing in UI**: Ensure `config_flow: true` is in manifest.json and restart Home Assistant

## Issues & Support

Report issues at: [GitHub Issues](https://github.com/thegogz/pixels_dice/issues)
