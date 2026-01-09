#!/bin/bash
# HyperSync Consensus-Tier Integration Deployment Script

set -e

echo "=========================================="
echo "HyperSync Consensus-Tier Integration"
echo "Deployment Script v1.0.0"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
        log_error "Python 3.8+ is required (found $PYTHON_VERSION)"
        exit 1
    fi

    log_info "Prerequisites OK"
}

# Extract patches
extract_patches() {
    log_info "Extracting patches..."

    PATCHES=(
        "PATCH-1-CONSENSUS-TIER-MAPPING.20251118.zip"
        "PATCH-2-CONSENSUS-SELECTION-API.20251118.zip"
        "PATCH-3-CONSENSUS-SELECTION-CLI.20251118.zip"
        "PATCH-4-CONSENSUS-CONFIG-VALIDATION.20251118.zip"
        "PATCH-5-CONSENSUS-TIER-DOCUMENTATION.20251118.zip"
    )

    for patch in "${PATCHES[@]}"; do
        if [ -f "$patch" ]; then
            log_info "Extracting $patch..."
            unzip -q -o "$patch" -d "${patch%.zip}/"
        else
            log_warn "Patch $patch not found, skipping"
        fi
    done

    log_info "Patches extracted"
}

# Install tier mapping
install_tier_mapping() {
    log_info "Installing tier mapping..."

    # Create directories
    mkdir -p planner/routing/
    mkdir -p schemas/
    mkdir -p consensus/installation_manifests/

    # Copy tier mapping
    if [ -f "PATCH-1-CONSENSUS-TIER-MAPPING.20251118/consensus/tier_mapping.json" ]; then
        cp PATCH-1-CONSENSUS-TIER-MAPPING.20251118/consensus/tier_mapping.json \
           planner/routing/hypersync_routing.tiers.json
        log_info "Tier mapping installed"
    else
        log_error "Tier mapping file not found"
        exit 1
    fi

    # Copy schemas
    cp PATCH-1-CONSENSUS-TIER-MAPPING.20251118/schemas/*.json schemas/

    # Copy installation manifests
    cp PATCH-1-CONSENSUS-TIER-MAPPING.20251118/consensus/installation_manifests/*.json \
       consensus/installation_manifests/

    log_info "Tier mapping installation complete"
}

# Install API layer
install_api() {
    log_info "Installing API layer..."

    mkdir -p api/consensus/
    mkdir -p api/consensus/middleware/
    mkdir -p api/consensus/handlers/
    mkdir -p api/consensus/tests/

    # Copy API files
    cp -r PATCH-2-CONSENSUS-SELECTION-API.20251118/api/consensus/* api/consensus/

    log_info "API layer installed"
}

# Install CLI layer
install_cli() {
    log_info "Installing CLI layer..."

    mkdir -p cli/consensus/
    mkdir -p cli/consensus/formatters/
    mkdir -p cli/consensus/tests/

    # Copy CLI files
    cp -r PATCH-3-CONSENSUS-SELECTION-CLI.20251118/cli/consensus/* cli/consensus/

    # Make CLI scripts executable
    chmod +x cli/consensus/*.py

    log_info "CLI layer installed"
}

# Install configuration
install_config() {
    log_info "Installing configuration..."

    mkdir -p config/consensus/default_configs/

    # Copy configuration files
    cp -r PATCH-4-CONSENSUS-CONFIG-VALIDATION.20251118/config/consensus/* config/consensus/

    log_info "Configuration installed"
}

# Install documentation
install_docs() {
    log_info "Installing documentation..."

    mkdir -p docs/consensus/tutorials/
    mkdir -p docs/consensus/examples/

    # Copy documentation
    cp -r PATCH-5-CONSENSUS-TIER-DOCUMENTATION.20251118/docs/consensus/* docs/consensus/

    log_info "Documentation installed"
}

# Run tests
run_tests() {
    log_info "Running integration tests..."

    # Run tier mapping tests
    if [ -f "tests/integration/test_tier_mapping.py" ]; then
        python3 -m pytest tests/integration/test_tier_mapping.py -v
    fi

    # Run API tests
    if [ -f "tests/integration/test_api_integration.py" ]; then
        python3 -m pytest tests/integration/test_api_integration.py -v
    fi

    log_info "Tests complete"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    # Check critical files
    CRITICAL_FILES=(
        "planner/routing/hypersync_routing.tiers.json"
        "schemas/consensus.schema.json"
        "api/consensus/list_mechanisms.py"
        "cli/consensus/list.py"
        "config/consensus/validation_rules.json"
        "docs/consensus/CONSENSUS_TIER_GUIDE.md"
    )

    for file in "${CRITICAL_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Critical file missing: $file"
            exit 1
        fi
    done

    log_info "Installation verified"
}

# Main deployment
main() {
    echo ""
    log_info "Starting deployment..."
    echo ""

    check_prerequisites
    extract_patches
    install_tier_mapping
    install_api
    install_cli
    install_config
    install_docs
    verify_installation

    echo ""
    log_info "=========================================="
    log_info "Deployment Complete!"
    log_info "=========================================="
    echo ""
    log_info "Next steps:"
    echo "  1. Review documentation: docs/consensus/CONSENSUS_TIER_GUIDE.md"
    echo "  2. Check your tier: hypersync tier info <tier>"
    echo "  3. List mechanisms: hypersync consensus list <tier>"
    echo "  4. Select mechanism: hypersync consensus select <mechanism> <tier>"
    echo ""
    log_info "For help: hypersync consensus --help"
    echo ""
}

# Run main
main
