# Deployment Scripts

These scripts help you quickly deploy the Pixels Dice integration to your Home Assistant instance.

## Prerequisites

1. **SSH Access**: Ensure you have SSH access to your Home Assistant instance
2. **SSH Key**: Set up SSH key authentication (recommended) or you'll be prompted for passwords
3. **Git Bash**: These scripts are designed for Git Bash on Windows

## First Time Setup

### 1. Create your `.env` file:
```bash
cd scripts
cp .env.example .env
# Edit .env with your hostnames, usernames, and paths
```

### 2. Make scripts executable:
```bash
chmod +x scripts/*.sh
```

## Scripts

### `deploy-direct.sh` (Recommended)

Deploys directly from your machine to Home Assistant.

**Usage:**
```bash
cd scripts
./deploy-direct.sh
```

**`.env` variables used:** `HA_HOST`, `HA_USER`, `HA_CONFIG_PATH`, `DOCKER_PATH`, `DOCKER_CONTAINER`

### `deploy.sh`

Deploys via NAS as an intermediary step.

**Usage:**
```bash
cd scripts
./deploy.sh
```

**`.env` variables used:** `NAS_HOST`, `NAS_USER`, `NAS_TEMP_PATH`, `HA_APPLIANCE_HOST`, `HA_APPLIANCE_USER`, `HA_APPLIANCE_CONFIG_PATH`

### 2. Set up SSH key authentication (optional but recommended):

**For Home Assistant:**
```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to Home Assistant
ssh-copy-id thegogz@homeassistant.local
```

**For NAS (if using deploy.sh):**
```bash
ssh-copy-id thegogz@gogznas.local
```

### 3. Test SSH connection:
```bash
ssh thegogz@homeassistant.local "ls -la /config"
```

## What the scripts do

1. **Verify** source directory exists
2. **Remove** old version from Home Assistant (if exists)
3. **Copy** new integration files to Home Assistant
4. **Set** correct permissions
5. **Prompt** to restart Home Assistant (optional)

## After Deployment

1. Restart Home Assistant (via script prompt or manually)
2. Go to **Settings** → **Devices & Services** → **Add Integration**
3. Search for "Pixels Dice"
4. Complete setup
5. Configure your dice to use webhook: `/api/webhook/pixels_dice`

## Troubleshooting

### "Permission denied (publickey)"
- Set up SSH key authentication (see above)
- Or check your username is correct

### "No such file or directory"
- Verify `HA_CONFIG_PATH` is correct for your Home Assistant installation
- For Home Assistant OS, it's typically `/config/custom_components`
- For Docker, it might be different

### "Permission denied" on Docker commands
- Docker requires `sudo` on most NAS setups. The scripts handle this automatically.
- Ensure your user has passwordless `sudo` for the docker binary (see sudoers.d config).
- Verify `DOCKER_PATH` in `.env` matches your system (find it with `which docker` or `find / -name docker -type f`).

### "Failed to restart container" or Docker errors
- Check your container name with: `ssh thegogz@gogznas.local "sudo /path/to/docker ps"`
- Update `DOCKER_CONTAINER` and `DOCKER_PATH` in `.env`
- Alternative: Restart via Home Assistant UI (**Settings** → **System** → **Restart**)

### Script won't run / syntax errors
- Make sure you're using Git Bash, not Windows CMD
- Run `dos2unix deploy-direct.sh` if you get line ending errors
- Ensure script is executable: `chmod +x deploy-direct.sh`

## Quick Reference

```bash
# Navigate to scripts directory
cd /c/Users/thego/Repos/pixels_dice/scripts

# Deploy directly to Home Assistant
./deploy-direct.sh

# Or deploy via NAS
./deploy.sh

# Just restart Home Assistant (no deployment) - fast method
ssh thegogz@gogznas.local 'sudo /path/to/docker exec homeassistant ha core restart'

# Or restart the entire Docker container - slower method
ssh thegogz@gogznas.local 'sudo /path/to/docker restart homeassistant'

# List running Docker containers
ssh thegogz@gogznas.local 'sudo /path/to/docker ps'
```
