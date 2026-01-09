"""
HyperSync Bootstrap Wizard

Interactive setup for first-run configuration, including provider registration.
"""

import asyncio
import os
import sys
from typing import Dict, Optional, List
from pathlib import Path
import json

from hypersync.providers import (
    ProviderConfig,
    ProviderCapability,
    get_registry
)
from hypersync.providers.adapters.factory import AdapterFactory


class BootstrapWizard:
    """
    Interactive wizard for HyperSync initialization.

    Guides users through:
    - Provider setup (ChatLLM, OpenAI, etc.)
    - API key configuration
    - Health checks
    - Initial sync
    """

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".hypersync"
        self.config_file = self.config_dir / "providers.json"
        self.providers_config: Dict = {}

    async def run(self):
        """Run the bootstrap wizard."""
        print("=" * 80)
        print("🚀 HyperSync Bootstrap Wizard")
        print("=" * 80)
        print()

        # Check if already configured
        if self.config_file.exists():
            print("⚠️  Existing configuration found.")
            response = input("Do you want to reconfigure? (y/N): ").strip().lower()
            if response != 'y':
                print("Exiting wizard.")
                return

        # Create config directory
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Provider setup
        await self._setup_providers()

        # Save configuration
        self._save_config()

        # Run health checks
        await self._health_checks()

        print()
        print("=" * 80)
        print("✅ Bootstrap Complete!")
        print("=" * 80)
        print()
        print(f"Configuration saved to: {self.config_file}")
        print()
        print("Next steps:")
        print("  • Run 'hypersync status' to check system health")
        print("  • Run 'hypersync prompt --help' for prompt routing")
        print("  • See docs at: docs/quickstart.md")
        print()

    async def _setup_providers(self):
        """Interactive provider setup."""
        print("
📦 Provider Setup")
        print("-" * 80)
        print()
        print("HyperSync can integrate with multiple cloud providers.")
        print("Let's configure your providers now.")
        print()

        # ChatLLM setup (recommended)
        setup_chatllm = input("Configure ChatLLM (Abacus.AI)? (Y/n): ").strip().lower()
        if setup_chatllm != 'n':
            await self._setup_chatllm()

        # OpenAI setup (optional)
        setup_openai = input("
Configure OpenAI? (y/N): ").strip().lower()
        if setup_openai == 'y':
            await self._setup_openai()

        # Anthropic setup (optional)
        setup_anthropic = input("
Configure Anthropic? (y/N): ").strip().lower()
        if setup_anthropic == 'y':
            await self._setup_anthropic()

        if not self.providers_config:
            print("
⚠️  No providers configured. You can add them later.")

    async def _setup_chatllm(self):
        """Setup ChatLLM provider."""
        print("
🔧 ChatLLM Configuration")
        print("-" * 40)
        print()
        print("Get your API key from: https://apps.abacus.ai/chatllm/admin/profile")
        print()

        api_key = input("ChatLLM API Key: ").strip()
        if not api_key:
            print("⚠️  Skipping ChatLLM setup (no API key provided)")
            return

        # Optional: custom API base
        api_base = input("API Base URL (press Enter for default): ").strip()
        if not api_base:
            api_base = "https://api.abacus.ai/v1"

        # Store configuration
        self.providers_config["chatllm"] = {
            "provider_id": "chatllm",
            "adapter_class": "chatllm",
            "api_key": api_key,
            "api_base": api_base,
            "timeout": 30,
            "max_retries": 3,
            "enabled": True
        }

        print("✓ ChatLLM configured")

    async def _setup_openai(self):
        """Setup OpenAI provider."""
        print("
🔧 OpenAI Configuration")
        print("-" * 40)
        print()

        api_key = input("OpenAI API Key: ").strip()
        if not api_key:
            print("⚠️  Skipping OpenAI setup")
            return

        self.providers_config["openai"] = {
            "provider_id": "openai",
            "adapter_class": "openai",
            "api_key": api_key,
            "api_base": "https://api.openai.com/v1",
            "timeout": 30,
            "max_retries": 3,
            "enabled": True
        }

        print("✓ OpenAI configured")

    async def _setup_anthropic(self):
        """Setup Anthropic provider."""
        print("
🔧 Anthropic Configuration")
        print("-" * 40)
        print()

        api_key = input("Anthropic API Key: ").strip()
        if not api_key:
            print("⚠️  Skipping Anthropic setup")
            return

        self.providers_config["anthropic"] = {
            "provider_id": "anthropic",
            "adapter_class": "anthropic",
            "api_key": api_key,
            "api_base": "https://api.anthropic.com/v1",
            "timeout": 30,
            "max_retries": 3,
            "enabled": True
        }

        print("✓ Anthropic configured")

    def _save_config(self):
        """Save provider configuration to disk."""
        config = {
            "version": "1.0",
            "providers": self.providers_config
        }

        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

        # Set restrictive permissions (user read/write only)
        os.chmod(self.config_file, 0o600)

    async def _health_checks(self):
        """Run health checks on configured providers."""
        if not self.providers_config:
            return

        print("
🏥 Running Health Checks")
        print("-" * 80)
        print()

        registry = get_registry()

        for provider_id, config_dict in self.providers_config.items():
            if not config_dict.get("enabled"):
                continue

            print(f"Checking {provider_id}...", end=" ")
            sys.stdout.flush()

            try:
                # Create adapter
                adapter = AdapterFactory.create_from_dict(
                    config_dict["adapter_class"],
                    config_dict
                )

                # Initialize
                success = await adapter.initialize()
                if not success:
                    print("❌ Failed to initialize")
                    continue

                # Health check
                status = await adapter.health_check()

                if status.value == "healthy":
                    print("✅ Healthy")
                elif status.value == "degraded":
                    print("⚠️  Degraded")
                elif status.value == "unauthorized":
                    print("❌ Unauthorized (check API key)")
                else:
                    print(f"❌ {status.value}")

                # Cleanup
                await adapter.shutdown()

            except Exception as e:
                print(f"❌ Error: {e}")


async def run_bootstrap():
    """Entry point for bootstrap wizard."""
    wizard = BootstrapWizard()
    await wizard.run()


if __name__ == "__main__":
    asyncio.run(run_bootstrap())
