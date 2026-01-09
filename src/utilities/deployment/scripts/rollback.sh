#!/bin/bash
# HyperSync Consensus-Tier Integration Rollback Script

set -e

echo "=========================================="
echo "HyperSync Consensus-Tier Integration"
echo "Rollback Script v1.0.0"
echo "=========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Backup current state
backup_current() {
    log_info "Backing up current state..."

    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    # Backup directories
    DIRS=(
        "planner/routing/"
        "schemas/"
        "consensus/"
        "api/consensus/"
        "cli/consensus/"
        "config/consensus/"
        "docs/consensus/"
    )

    for dir in "${DIRS[@]}"; do
        if [ -d "$dir" ]; then
            cp -r "$dir" "$BACKUP_DIR/"
        fi
    done

    log_info "Backup created: $BACKUP_DIR"
}

# Remove installed files
remove_files() {
    log_info "Removing installed files..."

    # Remove tier mapping
    rm -f planner/routing/hypersync_routing.tiers.json

    # Remove schemas
    rm -f schemas/consensus.schema.json
    rm -f schemas/consensus_validation.schema.json

    # Remove consensus directory
    rm -rf consensus/

    # Remove API
    rm -rf api/consensus/

    # Remove CLI
    rm -rf cli/consensus/

    # Remove config
    rm -rf config/consensus/

    # Remove docs
    rm -rf docs/consensus/

    log_info "Files removed"
}

# Restore from backup
restore_backup() {
    if [ -z "$1" ]; then
        log_error "No backup directory specified"
        exit 1
    fi

    BACKUP_DIR="$1"

    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "Backup directory not found: $BACKUP_DIR"
        exit 1
    fi

    log_info "Restoring from backup: $BACKUP_DIR"

    # Restore directories
    cp -r "$BACKUP_DIR"/* ./

    log_info "Restore complete"
}

# Main rollback
main() {
    echo ""
    log_warn "This will remove the consensus-tier integration"
    read -p "Continue? (y/N) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rollback cancelled"
        exit 0
    fi

    backup_current
    remove_files

    echo ""
    log_info "=========================================="
    log_info "Rollback Complete!"
    log_info "=========================================="
    echo ""
    log_info "Backup saved for restore if needed"
    echo ""
}

# Check for restore flag
if [ "$1" == "--restore" ]; then
    restore_backup "$2"
else
    main
fi
