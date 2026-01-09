"""
Environment Profile Manager
Manages optional environment profiles that agents can opt into.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentProfile:
    """Environment profile definition"""
    profile_id: str
    name: str
    version: str
    description: str = ""
    packages: List[Dict] = field(default_factory=list)
    config_files: List[Dict] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    services: List[Dict] = field(default_factory=list)
    scripts: List[Dict] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "packages": self.packages,
            "config_files": self.config_files,
            "environment_vars": self.environment_vars,
            "services": self.services,
            "scripts": self.scripts,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EnvironmentProfile':
        return cls(
            profile_id=data["profile_id"],
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            packages=data.get("packages", []),
            config_files=data.get("config_files", []),
            environment_vars=data.get("environment_vars", {}),
            services=data.get("services", []),
            scripts=data.get("scripts", []),
            dependencies=data.get("dependencies", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class ProfileActivation:
    """Record of profile activation"""
    activation_id: str
    profile_id: str
    agent_id: str
    sandbox_id: str
    activated_at: datetime
    status: str  # "active", "failed", "deactivated"
    installed_packages: List[str] = field(default_factory=list)
    created_files: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "activation_id": self.activation_id,
            "profile_id": self.profile_id,
            "agent_id": self.agent_id,
            "sandbox_id": self.sandbox_id,
            "activated_at": self.activated_at.isoformat(),
            "status": self.status,
            "installed_packages": self.installed_packages,
            "created_files": self.created_files,
            "error": self.error
        }


class ProfileManager:
    """Manages environment profiles"""

    def __init__(self, profiles_dir: str = "profiles"):
        """
        Initialize profile manager.

        Args:
            profiles_dir: Directory containing profile definitions
        """
        self.profiles_dir = profiles_dir
        self.profiles: Dict[str, EnvironmentProfile] = {}
        self.activations: List[ProfileActivation] = []

        # Load profiles from directory
        self._load_profiles()

        logger.info(f"ProfileManager initialized with {len(self.profiles)} profiles")

    def _load_profiles(self):
        """Load all profiles from profiles directory"""
        if not os.path.exists(self.profiles_dir):
            logger.warning(f"Profiles directory not found: {self.profiles_dir}")
            return

        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.profiles_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)

                    profile = EnvironmentProfile.from_dict(data)
                    self.profiles[profile.profile_id] = profile
                    logger.info(f"Loaded profile: {profile.profile_id}")

                except Exception as e:
                    logger.error(f"Failed to load profile {filename}: {e}")

    def get_profile(self, profile_id: str) -> Optional[EnvironmentProfile]:
        """Get profile by ID"""
        return self.profiles.get(profile_id)

    def list_profiles(self, tags: Optional[List[str]] = None) -> List[EnvironmentProfile]:
        """
        List available profiles.

        Args:
            tags: Optional list of tags to filter by

        Returns:
            List of profiles
        """
        profiles = list(self.profiles.values())

        if tags:
            profiles = [
                p for p in profiles
                if any(tag in p.tags for tag in tags)
            ]

        return profiles

    def activate_profile(
        self,
        profile_id: str,
        agent_id: str,
        sandbox_id: str,
        fs_adapter=None,
        process_manager=None,
        dry_run: bool = False
    ) -> ProfileActivation:
        """
        Activate a profile for an agent.

        Args:
            profile_id: Profile to activate
            agent_id: Agent ID
            sandbox_id: Sandbox ID
            fs_adapter: Filesystem adapter for file operations
            process_manager: Process manager for running scripts
            dry_run: If True, don't actually install anything

        Returns:
            ProfileActivation record
        """
        profile = self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile not found: {profile_id}")

        activation_id = f"activation-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        logger.info(f"Activating profile {profile_id} for agent {agent_id}")

        activation = ProfileActivation(
            activation_id=activation_id,
            profile_id=profile_id,
            agent_id=agent_id,
            sandbox_id=sandbox_id,
            activated_at=datetime.utcnow(),
            status="active"
        )

        try:
            # Resolve dependencies first
            if profile.dependencies:
                logger.info(f"Resolving {len(profile.dependencies)} dependencies")
                for dep_id in profile.dependencies:
                    dep_activation = self.activate_profile(
                        dep_id,
                        agent_id,
                        sandbox_id,
                        fs_adapter,
                        process_manager,
                        dry_run
                    )
                    if dep_activation.status == "failed":
                        raise Exception(f"Dependency failed: {dep_id}")

            # Install packages
            if profile.packages and not dry_run:
                logger.info(f"Installing {len(profile.packages)} packages")
                for pkg in profile.packages:
                    self._install_package(pkg, process_manager)
                    activation.installed_packages.append(pkg["name"])

            # Create config files
            if profile.config_files and not dry_run:
                logger.info(f"Creating {len(profile.config_files)} config files")
                for cfg in profile.config_files:
                    self._create_config_file(cfg, fs_adapter)
                    activation.created_files.append(cfg["path"])

            # Run setup scripts
            if profile.scripts and not dry_run:
                logger.info(f"Running {len(profile.scripts)} setup scripts")
                for script in profile.scripts:
                    self._run_script(script, process_manager)

            logger.info(f"Profile {profile_id} activated successfully")

        except Exception as e:
            logger.error(f"Profile activation failed: {e}")
            activation.status = "failed"
            activation.error = str(e)

        self.activations.append(activation)
        return activation

    def _install_package(self, pkg: Dict, process_manager):
        """Install a package"""
        if not process_manager:
            logger.warning("No process manager, skipping package install")
            return

        name = pkg["name"]
        manager = pkg.get("manager", "apt")
        version = pkg.get("version")

        # Build install command
        if manager == "apt":
            cmd = ["apt-get", "install", "-y", name]
        elif manager == "pip":
            cmd = ["pip", "install", name]
            if version:
                cmd[-1] = f"{name}=={version}"
        elif manager == "npm":
            cmd = ["npm", "install", "-g", name]
            if version:
                cmd[-1] = f"{name}@{version}"
        elif manager == "cargo":
            cmd = ["cargo", "install", name]
        else:
            logger.warning(f"Unknown package manager: {manager}")
            return

        logger.info(f"Installing package: {name} via {manager}")
        result = process_manager.run(cmd, timeout=300.0)

        if not result.success:
            raise Exception(f"Package install failed: {result.stderr}")

    def _create_config_file(self, cfg: Dict, fs_adapter):
        """Create a configuration file"""
        if not fs_adapter:
            logger.warning("No filesystem adapter, skipping config file")
            return

        path = cfg["path"]
        content = cfg["content"]
        mode = cfg.get("mode")

        # Expand home directory
        path = os.path.expanduser(path)

        logger.info(f"Creating config file: {path}")
        fs_adapter.write_text(path, content)

        # Set permissions if specified
        if mode and hasattr(os, 'chmod'):
            os.chmod(path, int(mode, 8))

    def _run_script(self, script: Dict, process_manager):
        """Run a setup script"""
        if not process_manager:
            logger.warning("No process manager, skipping script")
            return

        name = script["name"]
        content = script["content"]
        interpreter = script.get("interpreter", "bash")

        logger.info(f"Running script: {name}")

        # Write script to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(content)
            script_path = f.name

        try:
            # Make executable
            os.chmod(script_path, 0o755)

            # Run script
            result = process_manager.run([interpreter, script_path], timeout=300.0)

            if not result.success:
                raise Exception(f"Script failed: {result.stderr}")
        finally:
            # Clean up
            os.unlink(script_path)

    def deactivate_profile(self, activation_id: str) -> bool:
        """
        Deactivate a profile.

        Args:
            activation_id: Activation to deactivate

        Returns:
            True if deactivated, False if not found
        """
        for activation in self.activations:
            if activation.activation_id == activation_id:
                activation.status = "deactivated"
                logger.info(f"Deactivated profile: {activation.profile_id}")
                return True

        return False

    def get_activations(
        self,
        agent_id: Optional[str] = None,
        profile_id: Optional[str] = None
    ) -> List[ProfileActivation]:
        """Get profile activations"""
        activations = self.activations

        if agent_id:
            activations = [a for a in activations if a.agent_id == agent_id]

        if profile_id:
            activations = [a for a in activations if a.profile_id == profile_id]

        return activations

    def get_stats(self) -> Dict:
        """Get profile manager statistics"""
        total_profiles = len(self.profiles)
        total_activations = len(self.activations)
        active = sum(1 for a in self.activations if a.status == "active")
        failed = sum(1 for a in self.activations if a.status == "failed")

        return {
            "total_profiles": total_profiles,
            "total_activations": total_activations,
            "active_activations": active,
            "failed_activations": failed
        }


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    manager = ProfileManager(profiles_dir="profiles")

    # List profiles
    profiles = manager.list_profiles()
    print(f"Available profiles: {len(profiles)}")
    for p in profiles:
        print(f"  - {p.profile_id}: {p.name}")

    # Get specific profile
    profile = manager.get_profile("profile-python-dev")
    if profile:
        print(f"\nProfile: {profile.name}")
        print(f"Packages: {len(profile.packages)}")
        print(f"Config files: {len(profile.config_files)}")
