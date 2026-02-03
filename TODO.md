# Pixels Dice Integration - TODO List

Future enhancements and improvements for the Pixels Dice Home Assistant integration.

## Priority Order

1. **[HIGH]** Code Review for HA Standards
2. **[MEDIUM]** Dice Roll Automation Blueprints
3. **[MEDIUM]** Battery Status Tracking & Notifications
4. **[LOW]** HACS Publication Preparation

---

## 1. Code Review for HA Standards [HIGH PRIORITY]

Review and update the codebase to meet current Home Assistant quality standards.

### Quality Scale Requirements
- [ ] Review [HA Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale_index/)
- [ ] Check against Integration Quality Checklist
- [ ] Ensure we meet at least Bronze level requirements
- [ ] Document quality scale tier we're targeting

### Code Quality
- [x] Type hints (DONE)
- [x] Logging (DONE)
- [x] Modern entity patterns (DONE)
- [ ] Add docstrings to all functions
- [ ] Review error handling completeness
- [ ] Add input validation where needed
- [ ] Code organization review

### Testing
- [ ] Add unit tests for webhook handler
- [ ] Add unit tests for entity creation
- [ ] Add integration tests
- [ ] Test coverage report
- [ ] Add test fixtures

### Documentation
- [x] Basic README (DONE)
- [ ] Add screenshots to README
- [ ] Add integration logo/icon
- [ ] API documentation
- [ ] Developer documentation
- [ ] User guide

### Standards Compliance
- [ ] Review manifest.json completeness
- [ ] Check translations support
- [ ] Verify entity naming conventions
- [ ] Device registry best practices
- [ ] Entity registry best practices
- [ ] State class review

---

## 2. Dice Roll Automation Blueprints [MEDIUM PRIORITY]

Create Home Assistant automation blueprints for dice roll interactions.

### Blueprint Features
- [ ] Create blueprint for dice roll automation
- [ ] Allow selection of dice entity
- [ ] Support result-based conditions (e.g., "1-4", "5+", "equals 20")
- [ ] Dynamic handling based on die type (d6, d20, etc.)
- [ ] Support multiple action types based on roll results

### Implementation Details
- [ ] Blueprint should detect die type from device model
- [ ] Generate appropriate selectors for roll values (1-6 for d6, 1-20 for d20, etc.)
- [ ] Support range conditions (e.g., "between 1 and 4")
- [ ] Support comparison conditions (e.g., "greater than 15")
- [ ] Support exact match conditions (e.g., "equals 1" for critical fail)

### Example Use Cases
- [ ] D20 combat automation (18+ triggers "critical hit" notification)
- [ ] D6 random event selector (1-2 = event A, 3-4 = event B, 5-6 = event C)
- [ ] Dice game integration (track scores, trigger lights/sounds)
- [ ] Tabletop RPG helpers (auto-calculate modifiers, track initiative)

### Files to Create
- [ ] `blueprints/automation/pixels_dice/roll_action.yaml`
- [ ] Documentation for blueprint usage
- [ ] Example automations in README

---

## 3. Battery Status Tracking & Notifications [MEDIUM PRIORITY]

Add proper battery monitoring with low battery alerts.

### Battery Sensor Implementation
- [ ] Create separate battery sensor entity class
- [ ] Use `SensorDeviceClass.BATTERY`
- [ ] Set proper state class and unit of measurement
- [ ] Add battery percentage icon/display
- [ ] Update webhook to handle battery separately

### Entity Structure
Current: Each die has 1 entity (Roll Value)
Target: Each die has 2 entities:
- [ ] Roll Value sensor (existing)
- [ ] Battery sensor (new)

### Low Battery Notifications
- [ ] Add low battery threshold configuration (default 20%)
- [ ] Create binary sensor for "low battery" status
- [ ] Add automation blueprint for notifications
- [ ] Document how users can set up alerts

### Diagnostic Entities
Consider adding:
- [ ] Last roll timestamp
- [ ] Connection status
- [ ] Signal strength (if available)

### Implementation Files to Modify
- [ ] `entity.py` - Create BatterySensor class
- [ ] `sensor.py` - Register battery sensors
- [ ] `webhook.py` - Handle battery updates separately
- [ ] `const.py` - Add battery thresholds

---

## 4. HACS Publication Preparation [LOW PRIORITY]

Prepare the integration for publication via HACS (Home Assistant Community Store).

### Repository Structure
- [ ] Ensure proper directory structure
- [ ] Add `.github` workflows if needed
- [ ] Add issue templates
- [ ] Add PR template

### HACS Configuration
- [ ] Create `hacs.json` file
- [ ] Set proper category (integration)
- [ ] Add repository topics
- [ ] Verify naming conventions

### Branding
- [ ] Create integration icon (SVG format)
- [ ] Create brand logo
- [ ] Add to manifest.json
- [ ] Add screenshots

### Versioning & Releases
- [ ] Set up semantic versioning
- [ ] Create CHANGELOG.md
- [ ] Add version tags
- [ ] Create first release (v1.0.0)

### Documentation for HACS
- [ ] Update README for HACS users
- [ ] Add installation instructions via HACS
- [ ] Add "Add to HACS" button
- [ ] Document configuration

### Validation
- [ ] Run HACS validation
- [ ] Test installation via HACS (custom repository first)
- [ ] Fix any validation errors
- [ ] Submit to HACS default repositories

### Files to Create
- [ ] `hacs.json`
- [ ] `CHANGELOG.md`
- [ ] `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] `.github/ISSUE_TEMPLATE/feature_request.md`
- [ ] `info.md` (HACS info panel)

---

## Nice-to-Have Features (Future Consideration)

### Advanced Features
- [ ] Roll statistics tracking
- [ ] Roll history
- [ ] Dice grouping/sets
- [ ] Custom animations via LED control
- [ ] Dice calibration integration

### Integrations
- [ ] Discord webhook for rolls
- [ ] Virtual tabletop integration
- [ ] Streaming overlays

### Configuration Options
- [ ] Configurable webhook path
- [ ] Roll event triggers
- [ ] Custom notification templates

---

## Current Status

### ✅ Completed
- Modern Home Assistant integration structure
- SensorEntity with device registry
- Fixed webhook URL (`/api/webhook/pixels_dice`)
- Proper entity lifecycle management
- Type hints and logging
- Device naming with die type
- Multi-dice support (tested with physical dice)
- Deployment scripts
- Basic README

### 🚧 Current State
- **Version**: 1.0.0 (functional)
- **Quality Level**: Bronze (estimated)
- **Publication**: Private/custom installation only
- **Testing**: Manual testing only

### 📋 Next Session Goals
When returning to this project:
1. Start with Priority #1 (Code Review for HA Standards)
2. Then Priority #2 (Dice Roll Automation Blueprints)
3. Focus on Quality Scale requirements
4. Add basic unit tests
5. Improve documentation

---

## Notes

- Integration is currently working and tested with real Pixels dice
- Webhook endpoint is stable and well-defined
- Device registry integration is functional
- Entity naming follows HA conventions
- Supports 27+ dice (full collection tested)

## Reference Links

- [HA Developer Docs](https://developers.home-assistant.io/)
- [HA Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale_index/)
- [HACS Documentation](https://hacs.xyz/)
- [HA Integration Checklist](https://developers.home-assistant.io/docs/creating_integration_manifest/)
