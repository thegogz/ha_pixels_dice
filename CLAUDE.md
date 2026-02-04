# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Home Assistant custom integration for Pixels smart dice. Dice send roll data via HTTP webhook to Home Assistant, which creates device/sensor entities for each die automatically. Written in Python, async-first, targeting HA 2026.2+.

**Version**: 1.0.0 | **Quality Level**: Bronze | **IoT Class**: local_push (no polling)

## Validation & CI

```bash
# Run tests (requires Linux/WSL — pytest-homeassistant-custom-component depends on fcntl)
pip install -r requirements_test.txt
pytest tests/ -v

# Run hassfest locally (requires Docker)
docker run --rm -v $(pwd):/github/workspace ghcr.io/home-assistant/hassfest
```

The GitHub Actions workflow (`.github/workflows/main.yml`) runs both hassfest and pytest on every push, PR, and daily at midnight UTC. Tests cannot run natively on Windows due to HA's dependency on `fcntl`.

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

## Tests

Tests live in `tests/` and use `pytest-homeassistant-custom-component` for HA fixtures.

- `conftest.py` - Shared fixtures: `auto_enable_custom_integrations`, `sample_webhook_payload`, `minimal_webhook_payload`
- `test_config_flow.py` - Full config flow coverage (form display, entry creation, duplicate abort)
- `test_init.py` - Setup/unload lifecycle tests
- `test_webhook.py` - Webhook validation: valid payload, updates, invalid JSON, missing fields, type validation, defaults

## Conventions

- All modules use `from __future__ import annotations` and full type hints
- All setup/handler methods are async
- Logging via module-level `_LOGGER = logging.getLogger(__name__)`
- Entity unique_id: `pixels_dice_{pixel_id}`
- No external dependencies (only HA core APIs)

## Deployment

Deploy scripts live in `scripts/` and require a `scripts/.env` file (copy from `.env.example`). The NAS runs HA Container (not HA OS), so restarts use `docker restart` — the `ha` CLI is not available.

```bash
# Deploy to HA and restart (interactive — prompts for restart)
bash scripts/deploy-direct.sh

# Manual restart only
ssh $HA_USER@$HA_HOST "sudo $DOCKER_PATH restart $DOCKER_CONTAINER"

# Manual webhook test
curl -X POST http://gogznas.local:8123/api/webhook/pixels_dice \
  -H "Content-Type: application/json" \
  -d '{"pixelId": 12345678, "pixelName": "Test D20", "faceValue": 20, "ledCount": 20, "dieType": "d20", "colorway": "onyxBlack", "batteryLevel": 0.85}'
```

After any significant change to `custom_components/pixels_dice/`, run `deploy-direct.sh` and verify the integration loads correctly before committing.

## Roadmap (from TODO.md)

1. ~~**[HIGH]** Code review for HA quality scale standards, add docstrings and unit tests~~ (Done)
2. **[MEDIUM]** Dice roll automation blueprints
3. **[MEDIUM]** Battery status as separate sensor entity with low-battery alerts
4. **[LOW]** HACS publication preparation
