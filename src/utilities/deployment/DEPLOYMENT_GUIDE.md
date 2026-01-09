# Deployment Guide: Consensus-Tier Integration

## Overview

This guide covers deploying the complete HyperSync Consensus-Tier Integration across all environments.

## Prerequisites

### System Requirements

- **Operating System:** Linux (Ubuntu 20.04+, CentOS 8+) or macOS 10.15+
- **Python:** 3.8 or higher
- **Disk Space:** 500 MB minimum
- **Memory:** 2 GB minimum
- **Network:** Internet connection for initial setup

### Software Requirements

```bash
# Python 3.8+
python3 --version

# pip
pip3 --version

# unzip
unzip -v

# Optional: pytest for running tests
pip3 install pytest
```

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

Use the provided deployment script for automated installation.

#### Step 1: Prepare Environment

```bash
# Create deployment directory
mkdir -p hypersync-consensus-deployment
cd hypersync-consensus-deployment

# Copy all patch files
cp /path/to/PATCH-*.zip .
cp /path/to/-INTEGRATION-TESTING.zip .

# Extract deployment scripts
unzip -INTEGRATION-TESTING.zip
```

#### Step 2: Run Deployment Script

```bash
# Make script executable
chmod +x deployment/scripts/deploy.sh

# Run deployment
./deployment/scripts/deploy.sh
```

The script will:
1. Check prerequisites
2. Extract all patches
3. Install tier mapping
4. Install API layer
5. Install CLI layer
6. Install configuration
7. Install documentation
8. Verify installation

#### Step 3: Validate Installation

```bash
# Run validation script
python3 deployment/scripts/validate.py
```

Expected output:
```
============================================================
HyperSync Consensus-Tier Integration Validation
============================================================

Validating Tier Mapping... ✓
Validating Resource Profiles... ✓
Validating Installation Manifests... ✓
Validating Schemas... ✓
Validating API Layer... ✓
Validating CLI Layer... ✓
Validating Configuration... ✓
Validating Documentation... ✓

============================================================
Validation Results
============================================================

✓ All validations passed!

Integration is correctly installed and ready to use.
```

---

### Method 2: Manual Deployment

For custom installations or troubleshooting.

#### Step 1: Extract Patches

```bash
# Extract each patch
unzip -CONSENSUS-TIER-MAPPING.20251118.zip -d /
unzip -CONSENSUS-SELECTION-API.20251118.zip -d /
unzip -CONSENSUS-SELECTION-CLI.20251118.zip -d /
unzip -CONSENSUS-CONFIG-VALIDATION.20251118.zip -d /
unzip -CONSENSUS-TIER-DOCUMENTATION.20251118.zip -d /
```

#### Step 2: Install Tier Mapping

```bash
# Create directories
mkdir -p planner/routing/
mkdir -p schemas/
mkdir -p consensus/installation_manifests/

# Copy tier mapping
cp /consensus/tier_mapping.json \
 planner/routing/hypersync_routing.tiers.json

# Copy schemas
cp /schemas/*.json schemas/

# Copy installation manifests
cp /consensus/installation_manifests/*.json \
 consensus/installation_manifests/
```

#### Step 3: Install API Layer

```bash
# Create directories
mkdir -p api/consensus/middleware/
mkdir -p api/consensus/handlers/
mkdir -p api/consensus/tests/

# Copy API files
cp -r /api/consensus/* api/consensus/
```

#### Step 4: Install CLI Layer

```bash
# Create directories
mkdir -p cli/consensus/formatters/
mkdir -p cli/consensus/tests/

# Copy CLI files
cp -r /cli/consensus/* cli/consensus/

# Make scripts executable
chmod +x cli/consensus/*.py
```

#### Step 5: Install Configuration

```bash
# Create directories
mkdir -p config/consensus/default_configs/

# Copy configuration
cp -r /config/consensus/* config/consensus/
```

#### Step 6: Install Documentation

```bash
# Create directories
mkdir -p docs/consensus/tutorials/
mkdir -p docs/consensus/examples/

# Copy documentation
cp -r /docs/consensus/* docs/consensus/
```

#### Step 7: Verify Installation

```bash
# Check critical files
ls -l planner/routing/hypersync_routing.tiers.json
ls -l api/consensus/list_mechanisms.py
ls -l cli/consensus/list.py
ls -l config/consensus/validation_rules.json
ls -l docs/consensus/CONSENSUS_TIER_GUIDE.md
```

---

## Post-Deployment Configuration

### 1. Environment Variables

Set optional environment variables:

```bash
# HyperSync home directory
export HYPERSYNC_HOME=/path/to/hypersync

# Default tier (optional)
export HYPERSYNC_DEFAULT_TIER=PRO

# API endpoint (if using remote API)
export HYPERSYNC_API_ENDPOINT=http://localhost:8000
```

### 2. Python Path

Add HyperSync to Python path:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PYTHONPATH=$PYTHONPATH:/path/to/hypersync
```

### 3. CLI Aliases

Create convenient aliases:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias hs-consensus='python3 /path/to/hypersync/cli/consensus/list.py'
alias hs-tier='python3 /path/to/hypersync/cli/consensus/tier_info.py'
```

---

## Verification

### Quick Verification

```bash
# Check tier mapping
cat planner/routing/hypersync_routing.tiers.json | jq '.tiers | keys'

# Expected output: ["CORE", "Basic", "PRO", "Advanced", "QM_Venture", "QM_Campaign", "QM_Imperium"]
```

### Comprehensive Verification

Run the validation script:

```bash
python3 deployment/scripts/validate.py
```

### Manual Verification

```bash
# Test API
python3 -c "from api.consensus.list_mechanisms import api_list_mechanisms; print(api_list_mechanisms('PRO'))"

# Test CLI
python3 cli/consensus/list.py PRO

# Check configuration
ls config/consensus/default_configs/ | wc -l
# Expected: 14 files
```

---

## Testing

### Unit Tests

```bash
# Run API tests
python3 -m pytest api/consensus/tests/ -v

# Run CLI tests
python3 -m pytest cli/consensus/tests/ -v
```

### Integration Tests

```bash
# Run integration tests
python3 -m pytest tests/integration/ -v
```

### End-to-End Tests

```bash
# Run E2E tests
python3 -m pytest tests/e2e/ -v
```

---

## Rollback

If you need to rollback the deployment:

### Automated Rollback

```bash
# Run rollback script
./deployment/scripts/rollback.sh
```

This will:
1. Backup current state
2. Remove all installed files
3. Save backup for potential restore

### Restore from Backup

```bash
# Restore from specific backup
./deployment/scripts/rollback.sh --restore backup_20251118_120000
```

### Manual Rollback

```bash
# Remove installed files
rm -rf planner/routing/hypersync_routing.tiers.json
rm -rf schemas/consensus*.json
rm -rf consensus/
rm -rf api/consensus/
rm -rf cli/consensus/
rm -rf config/consensus/
rm -rf docs/consensus/
```

---

## Troubleshooting

### Issue: Deployment Script Fails

**Symptom:** `deploy.sh` exits with error

**Solutions:**
1. Check prerequisites: `python3 --version`
2. Verify all patch files present: `ls PATCH-*.zip`
3. Check permissions: `chmod +x deployment/scripts/deploy.sh`
4. Review error messages in output

### Issue: Validation Fails

**Symptom:** `validate.py` reports errors

**Solutions:**
1. Check which validation failed
2. Verify file exists: `ls -l <file_path>`
3. Re-extract specific . Run manual deployment for failed component

### Issue: Import Errors

**Symptom:** `ModuleNotFoundError` when running scripts

**Solutions:**
1. Check Python path: `echo $PYTHONPATH`
2. Add HyperSync to path: `export PYTHONPATH=$PYTHONPATH:/path/to/hypersync`
3. Verify file structure: `ls -R api/consensus/`

### Issue: Permission Denied

**Symptom:** Cannot execute scripts

**Solutions:**
```bash
# Make scripts executable
chmod +x cli/consensus/*.py
chmod +x deployment/scripts/*.sh
chmod +x deployment/scripts/*.py
```

---

## Environment-Specific Deployment

### Development Environment

```bash
# Deploy with development settings
./deployment/scripts/deploy.sh

# Enable debug logging
export HYPERSYNC_DEBUG=1

# Use local configuration
export HYPERSYNC_CONFIG_PATH=./config/dev/
```

### Staging Environment

```bash
# Deploy to staging
./deployment/scripts/deploy.sh

# Use staging tier
export HYPERSYNC_DEFAULT_TIER=PRO

# Point to staging API
export HYPERSYNC_API_ENDPOINT=https://staging-api.hypersync.io
```

### Production Environment

```bash
# Deploy to production
./deployment/scripts/deploy.sh

# Use production tier
export HYPERSYNC_DEFAULT_TIER=Advanced

# Point to production API
export HYPERSYNC_API_ENDPOINT=https://api.hypersync.io

# Enable production logging
export HYPERSYNC_LOG_LEVEL=INFO
export HYPERSYNC_LOG_FILE=/var/log/hypersync/consensus.log
```

---

## Monitoring

### Health Checks

```bash
# Check tier mapping
python3 -c "import json; print(json.load(open('planner/routing/hypersync_routing.tiers.json'))['version'])"

# Check API health
python3 -c "from api.consensus.list_mechanisms import api_list_mechanisms; print(api_list_mechanisms('CORE')['status'])"

# Check CLI health
python3 cli/consensus/status.py --format json
```

### Logging

```bash
# Enable logging
export HYPERSYNC_LOG_LEVEL=DEBUG
export HYPERSYNC_LOG_FILE=/var/log/hypersync/consensus.log

# View logs
tail -f /var/log/hypersync/consensus.log
```

---

## Upgrade Path

### Upgrading from Previous Version

If upgrading from a previous consensus-tier integration:

1. **Backup current installation:**
 ```bash
 ./deployment/scripts/rollback.sh
 ```

2. **Deploy new version:**
 ```bash
 ./deployment/scripts/deploy.sh
 ```

3. **Migrate configuration:**
 ```bash
 # Export current config
 python3 cli/consensus/status.py --format json > current_config.json

 # Validate against new version
 python3 cli/consensus/validate.py <mechanism> <tier> "$(cat current_config.json)"
 ```

4. **Verify upgrade:**
 ```bash
 python3 deployment/scripts/validate.py
 ```

---

## Support

### Documentation

- **Main Guide:** `docs/consensus/CONSENSUS_TIER_GUIDE.md`
- **API Reference:** `/API_CONSENSUS_SELECTION_README.md`
- **CLI Reference:** `/CLI_CONSENSUS_COMMANDS_README.md`
- **Configuration:** `/CONFIG_CONSENSUS_README.md`

### Community

- **Forums:** https://community.hypersync.io
- **GitHub:** https://github.com/hypersync/consensus-tier-integration
- **Discord:** https://discord.gg/hypersync

### Professional Support

- **Email:** support@hypersync.io (Advanced+ tiers)
- **Priority Support:** Available for Advanced+ tiers
- **On-site Support:** Available for QM tiers

---

## Checklist

### Pre-Deployment

- [ ] System requirements met
- [ ] All patch files downloaded
- [ ] Backup of existing installation (if applicable)
- [ ] Deployment plan reviewed
- [ ] Maintenance window scheduled (if production)

### Deployment

- [ ] Patches extracted
- [ ] Tier mapping installed
- [ ] API layer installed
- [ ] CLI layer installed
- [ ] Configuration installed
- [ ] Documentation installed
- [ ] Installation validated

### Post-Deployment

- [ ] Environment variables configured
- [ ] Python path updated
- [ ] CLI aliases created
- [ ] Tests run successfully
- [ ] Health checks passing
- [ ] Documentation reviewed
- [ ] Team notified

---

*Part of the HyperSync Consensus-Tier Integration Series*
*Version 1.0.0 - 2025-11-18T18:36:27.094462*
