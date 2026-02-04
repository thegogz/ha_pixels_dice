#!/bin/bash
# Deployment script for Pixels Dice Home Assistant integration
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

# Map .env variables to this script's names
HA_HOST="${HA_APPLIANCE_HOST}"
HA_USER="${HA_APPLIANCE_USER}"
HA_CONFIG_PATH="${HA_APPLIANCE_CONFIG_PATH}"

# Source directory (relative to repo root)
SOURCE_DIR="custom_components/pixels_dice"

# =============================================================================
# SCRIPT
# =============================================================================

echo -e "${GREEN}Starting Pixels Dice deployment...${NC}"

# Get the repo root directory (one level up from scripts/)
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo -e "${YELLOW}Step 1/4: Verifying source directory...${NC}"
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}Error: Source directory $SOURCE_DIR not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Source directory found${NC}"

echo -e "${YELLOW}Step 2/4: Copying to NAS ($NAS_HOST)...${NC}"
# Create temp directory on NAS and copy files
ssh "${NAS_USER}@${NAS_HOST}" "mkdir -p ${NAS_TEMP_PATH}"
scp -r "$SOURCE_DIR" "${NAS_USER}@${NAS_HOST}:${NAS_TEMP_PATH}/"
echo -e "${GREEN}✓ Files copied to NAS${NC}"

echo -e "${YELLOW}Step 3/4: Deploying to Home Assistant ($HA_HOST)...${NC}"
# SSH to Home Assistant and copy from NAS
ssh "${HA_USER}@${HA_HOST}" << EOF
    # Create custom_components directory if it doesn't exist
    mkdir -p ${HA_CONFIG_PATH}

    # Remove old version if exists
    if [ -d "${HA_CONFIG_PATH}/pixels_dice" ]; then
        echo "Removing old version..."
        rm -rf ${HA_CONFIG_PATH}/pixels_dice
    fi

    # Copy from NAS to Home Assistant
    echo "Copying files from NAS..."
    scp -r ${NAS_USER}@${NAS_HOST}:${NAS_TEMP_PATH}/pixels_dice ${HA_CONFIG_PATH}/

    echo "Setting permissions..."
    chmod -R 755 ${HA_CONFIG_PATH}/pixels_dice
EOF
echo -e "${GREEN}✓ Deployed to Home Assistant${NC}"

echo -e "${YELLOW}Step 4/4: Cleaning up NAS temporary files...${NC}"
ssh "${NAS_USER}@${NAS_HOST}" "rm -rf ${NAS_TEMP_PATH}"
echo -e "${GREEN}✓ Cleanup complete${NC}"

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Restart Home Assistant"
echo "2. Go to Settings → Devices & Services → Add Integration"
echo "3. Search for 'Pixels Dice' and set it up"
echo ""
echo -e "${YELLOW}To restart Home Assistant from command line:${NC}"
echo "   ssh ${HA_USER}@${HA_HOST} 'ha core restart'"
echo ""
read -p "Would you like to restart Home Assistant now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Restarting Home Assistant...${NC}"
    ssh "${HA_USER}@${HA_HOST}" 'ha core restart' || echo -e "${RED}Note: 'ha' command not found. You may need to restart manually via the UI.${NC}"
    echo -e "${GREEN}✓ Restart initiated${NC}"
fi

echo -e "${GREEN}Done!${NC}"
