#!/usr/bin/env python3
"""
Validation Script: Verify Consensus-Tier Integration

Validates the complete integration is correctly installed.
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple

class ValidationError(Exception):
    """Validation error."""
    pass

class IntegrationValidator:
    """Validates consensus-tier integration."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> bool:
        """Run all validations."""
        print("="*60)
        print("HyperSync Consensus-Tier Integration Validation")
        print("="*60)
        print()

        validations = [
            ("Tier Mapping", self.validate_tier_mapping),
            ("Resource Profiles", self.validate_resource_profiles),
            ("Installation Manifests", self.validate_installation_manifests),
            ("Schemas", self.validate_schemas),
            ("API Layer", self.validate_api),
            ("CLI Layer", self.validate_cli),
            ("Configuration", self.validate_config),
            ("Documentation", self.validate_docs),
        ]

        for name, validator in validations:
            print(f"Validating {name}...", end=" ")
            try:
                validator()
                print("✓")
            except ValidationError as e:
                print("✗")
                self.errors.append(f"{name}: {e}")
            except Exception as e:
                print("✗")
                self.errors.append(f"{name}: Unexpected error: {e}")

        print()
        self.print_results()

        return len(self.errors) == 0

    def validate_tier_mapping(self):
        """Validate tier mapping file."""
        path = Path("planner/routing/hypersync_routing.tiers.json")
        if not path.exists():
            raise ValidationError("Tier mapping file not found")

        with open(path) as f:
            data = json.load(f)

        # Check required tiers
        required_tiers = ["CORE", "Basic", "PRO", "Advanced", 
                         "QM_Venture", "QM_Campaign", "QM_Imperium"]

        if 'tiers' not in data:
            raise ValidationError("Missing 'tiers' key")

        for tier in required_tiers:
            if tier not in data['tiers']:
                raise ValidationError(f"Missing tier: {tier}")

    def validate_resource_profiles(self):
        """Validate resource profiles."""
        path = Path("consensus/mechanism_profiles.json")
        if not path.exists():
            raise ValidationError("Resource profiles file not found")

        with open(path) as f:
            data = json.load(f)

        if 'profiles' not in data:
            raise ValidationError("Missing 'profiles' key")

        # Check all 14 mechanisms have profiles
        expected_count = 14
        actual_count = len(data['profiles'])

        if actual_count != expected_count:
            raise ValidationError(
                f"Expected {expected_count} profiles, found {actual_count}"
            )

    def validate_installation_manifests(self):
        """Validate installation manifests."""
        manifest_dir = Path("consensus/installation_manifests")
        if not manifest_dir.exists():
            raise ValidationError("Installation manifests directory not found")

        # Check all 7 tier manifests exist
        required_tiers = ["CORE", "Basic", "PRO", "Advanced",
                         "QM_Venture", "QM_Campaign", "QM_Imperium"]

        for tier in required_tiers:
            manifest_path = manifest_dir / f"{tier}_manifest.json"
            if not manifest_path.exists():
                raise ValidationError(f"Missing manifest for tier: {tier}")

    def validate_schemas(self):
        """Validate schemas."""
        schemas = [
            "schemas/consensus.schema.json",
            "schemas/consensus_validation.schema.json"
        ]

        for schema_path in schemas:
            path = Path(schema_path)
            if not path.exists():
                raise ValidationError(f"Schema not found: {schema_path}")

            # Validate JSON
            with open(path) as f:
                json.load(f)

    def validate_api(self):
        """Validate API layer."""
        api_files = [
            "api/consensus/list_mechanisms.py",
            "api/consensus/get_mechanism_info.py",
            "api/consensus/select_mechanism.py",
            "api/consensus/get_current_mechanism.py",
            "api/consensus/validate_mechanism_config.py",
            "api/consensus/tier_capabilities.py",
        ]

        for api_file in api_files:
            path = Path(api_file)
            if not path.exists():
                raise ValidationError(f"API file not found: {api_file}")

    def validate_cli(self):
        """Validate CLI layer."""
        cli_files = [
            "cli/consensus/list.py",
            "cli/consensus/info.py",
            "cli/consensus/select.py",
            "cli/consensus/status.py",
            "cli/consensus/validate.py",
            "cli/consensus/tier_info.py",
            "cli/consensus/compare.py",
            "cli/consensus/recommend.py",
        ]

        for cli_file in cli_files:
            path = Path(cli_file)
            if not path.exists():
                raise ValidationError(f"CLI file not found: {cli_file}")

    def validate_config(self):
        """Validate configuration."""
        config_dir = Path("config/consensus/default_configs")
        if not config_dir.exists():
            raise ValidationError("Default configs directory not found")

        # Check all 14 mechanism configs exist
        expected_count = 14
        actual_count = len(list(config_dir.glob("*.json")))

        if actual_count != expected_count:
            raise ValidationError(
                f"Expected {expected_count} configs, found {actual_count}"
            )

    def validate_docs(self):
        """Validate documentation."""
        docs = [
            "docs/consensus/CONSENSUS_TIER_GUIDE.md",
            "docs/consensus/MECHANISM_COMPARISON.md",
            "docs/consensus/TIER_SELECTION_GUIDE.md",
        ]

        for doc in docs:
            path = Path(doc)
            if not path.exists():
                raise ValidationError(f"Documentation not found: {doc}")

    def print_results(self):
        """Print validation results."""
        print("="*60)
        print("Validation Results")
        print("="*60)
        print()

        if self.errors:
            print(f"✗ {len(self.errors)} Error(s):")
            for error in self.errors:
                print(f"  • {error}")
            print()

        if self.warnings:
            print(f"⚠ {len(self.warnings)} Warning(s):")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        if not self.errors and not self.warnings:
            print("✓ All validations passed!")
            print()
            print("Integration is correctly installed and ready to use.")
        elif not self.errors:
            print("✓ Validation passed with warnings")
        else:
            print("✗ Validation failed")
            print()
            print("Please fix the errors and run validation again.")

        print()

def main():
    """Main entry point."""
    validator = IntegrationValidator()
    success = validator.validate_all()

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
