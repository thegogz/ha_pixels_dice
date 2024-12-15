Pixels Dice

A Home Assistant custom integration for tracking and managing Pixel Dice entities.

Features:
- Automatically creates entities for each Pixel Dice.
- Tracks roll results (face_value) as the entity state.
- Includes additional attributes like die_type, colorway, battery_level, and led_count.

Installation:
1. Copy the `pixels_dice` folder to your Home Assistant `custom_components` directory:

   custom_components/
   └── pixels_dice/
       ├── __init__.py
       ├── manifest.json
       ├── const.py
       ├── entity.py
       ├── config_flow.py
       ├── strings.json
       ├── webhook.py

2. Restart Home Assistant.
3. Go to "Settings > Devices & Services > Integrations" and click the "Add Integration" button.
4. Search for "Pixels Dice" and follow the prompts.

Webhook Configuration:
The integration uses a webhook to receive data from your Pixel Dice. Configure your Pixel Dice to send POST requests to:

http://<your_home_assistant_url>/api/webhook/pixels_dice

Ensure the data sent is in the following JSON format:

{
  "pixelId": 12345678,
  "pixelName": "Pixels D20",
  "faceValue": 20,
  "ledCount": 20,
  "dieType": "d20",
  "colorway": "onyxBlack",
  "batteryLevel": 0.5
}

Entity Attributes:
- State: The latest roll result (face_value).
- Attributes:
  - led_count: Number of LEDs on the dice.
  - die_type: Type of dice (e.g., d20, d6).
  - colorway: Color scheme of the dice.
  - battery_level: Remaining battery percentage.

Issues:
Report issues at: https://github.com/thegogz/pixels_dice/issues