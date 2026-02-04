# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Home Assistant custom integration for Pixels smart dice. Dice send roll data via HTTP webhook to Home Assistant, which creates device/sensor entities for each die automatically. Written in Python, async-first, targeting HA 2026.2+.

**Version**: 1.0.0 | **Quality Level**: Bronze (estimated) | **IoT Class**: local_push (no polling)

## Validation & CI

There is no local build, lint, or test suite. The only CI step is hassfest validation via GitHub Actions:

```bash
# Run hassfest locally (requires Docker)
docker run --rm -v $(pwd):/github/workspace ghcr.io/home-assistant/hassfest
```

The GitHub Actions workflow (`.github/workflows/main.yml`) runs hassfest on every push, PR, and daily at midnight UTC.

Manual webhook testing:
```bash
curl -X POST http://homeassistant.local:8123/api/webhook/pixels_dice \
  -H "Content-Type: application/json" \
  -d '{"pixelId": 12345678, "pixelName": "Test D20", "faceValue": 20, "ledCount": 20, "dieType": "d20", "colorway": "onyxBlack", "batteryLevel": 0.85}'
```

## Architecture

All integration code lives in `custom_components/pixels_dice/` (~296 lines total).

**Data flow**: Webhook HTTP POST -> `webhook.py` validates & parses -> creates/updates `PixelsDiceEntity` in `entity.py` -> entity registered via callback stored by `sensor.py`

**Key components**:
- `__init__.py` - Entry point. Sets up `hass.data[DOMAIN]` storage, registers webhook, forwards to sensor platform. Handles `async_setup_entry` / `async_unload_entry`.
- `webhook.py` - Registers fixed endpoint at `/api/webhook/pixels_dice`. Validates required fields (`pixelId`, `faceValue`, `ledCount`). Creates new `PixelsDiceEntity` on first contact or updates existing ones.
- `entity.py` - `PixelsDiceEntity(SensorEntity)` with `_attr_has_entity_name = True`, `_attr_should_poll = False`. State is the roll value. Extra attributes: `led_count`, `die_type`, `colorway`, `battery_level`. Each die becomes a device named `{DIE_TYPE} - {PIXEL_NAME}`.
- `sensor.py` - Platform setup. Stores the `async_add_entities` callback in `hass.data[DOMAIN]` for `webhook.py` to use later when new dice appear.
- `config_flow.py` - Single-instance only config flow (no user input required).
- `const.py` - Just `DOMAIN = "pixels_dice"`.

**Runtime data structure**:
```python
hass.data[DOMAIN][entry_id] = {
    "add_entities": <async_add_entities callback>,
    "entities": { pixel_id: PixelsDiceEntity, ... }
}
```

## Conventions

- All modules use `from __future__ import annotations` and full type hints
- All setup/handler methods are async
- Logging via module-level `_LOGGER = logging.getLogger(__name__)`
- Entity unique_id: `pixels_dice_{pixel_id}`
- No external dependencies (only HA core APIs)

## Deployment

Shell scripts in `scripts/` deploy via SSH to a Home Assistant Docker instance. Not relevant for development, only for the maintainer's home lab setup.

## Roadmap (from TODO.md)

1. **[HIGH]** Code review for HA quality scale standards, add docstrings and unit tests
2. **[MEDIUM]** Dice roll automation blueprints
3. **[MEDIUM]** Battery status as separate sensor entity with low-battery alerts
4. **[LOW]** HACS publication preparation
