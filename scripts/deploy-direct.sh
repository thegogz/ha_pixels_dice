#!/bin/bash
# Direct deployment script for Pixels Dice Home Assistant integration
# Deploys directly from your machine to Home Assistant (no NAS intermediary)
# Compatible with Git Bash on Windows

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# =============================================================================
# CONFIGURATION - Load from .env file
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${RED}Error: .env file not found. Copy .env.example to .env and fill in your values.${NC}"
    exit 1
fi
source "$SCRIPT_DIR/.env"

# Source directory (relative to repo root)
SOURCE_DIR="custom_components/pixels_dice"

# =============================================================================
# SCRIPT
# =============================================================================

echo -e "${GREEN}Starting Pixels Dice direct deployment...${NC}"

# Get the repo root directory (one level up from scripts/)
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo -e "${YELLOW}Step 1/3: Verifying source directory...${NC}"
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}Error: Source directory $SOURCE_DIR not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Source directory found${NC}"

echo -e "${YELLOW}Step 2/3: Deploying to Home Assistant ($HA_HOST)...${NC}"

# Remove old version on Home Assistant (docker-owned __pycache__ needs sudo)
echo "Removing old version (if exists)..."
ssh "${HA_USER}@${HA_HOST}" "mkdir -p ${HA_CONFIG_PATH} && sudo ${DOCKER_PATH} run --rm -v ${HA_CONFIG_PATH}:/mnt alpine rm -rf /mnt/pixels_dice" || true

# Copy new version (stage without __pycache__ first)
echo "Copying files..."
STAGING_DIR=$(mktemp -d)
cp -r "$SOURCE_DIR" "$STAGING_DIR/"
find "$STAGING_DIR" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
scp -r "$STAGING_DIR/pixels_dice" "${HA_USER}@${HA_HOST}:${HA_CONFIG_PATH}/"
rm -rf "$STAGING_DIR"

# Set permissions
echo "Setting permissions..."
ssh "${HA_USER}@${HA_HOST}" "chmod -R 755 ${HA_CONFIG_PATH}/pixels_dice"

echo -e "${GREEN}✓ Deployed to Home Assistant${NC}"

echo -e "${YELLOW}Step 3/3: Verifying installation...${NC}"
ssh "${HA_USER}@${HA_HOST}" "ls -la ${HA_CONFIG_PATH}/pixels_dice/" && echo -e "${GREEN}✓ Verification complete${NC}"

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Restart Home Assistant"
echo "2. Go to Settings → Devices & Services → Add Integration"
echo "3. Search for 'Pixels Dice' and set it up"
echo "4. Webhook URL: http://${HA_HOST}:8123/api/webhook/pixels_dice"
echo ""
echo -e "${YELLOW}To restart Home Assistant:${NC}"
echo "   ssh ${HA_USER}@${HA_HOST} 'sudo ${DOCKER_PATH} restart ${DOCKER_CONTAINER}'"
echo ""
read -p "Would you like to restart Home Assistant now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Restarting Home Assistant container...${NC}"
    if ssh "${HA_USER}@${HA_HOST}" "sudo ${DOCKER_PATH} restart ${DOCKER_CONTAINER}"; then
        echo -e "${GREEN}✓ Container restarted successfully${NC}"
        echo -e "${YELLOW}Note: Home Assistant may take 30-60 seconds to fully start${NC}"
    else
        echo -e "${RED}Failed to restart${NC}"
        echo -e "${YELLOW}Restart manually via HA UI: Settings → System → Restart${NC}"
    fi
fi

echo -e "${GREEN}Done!${NC}"
