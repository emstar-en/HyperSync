"""
HyperSync Agent Profile Registry

Provides CRUD operations, validation, and versioning for agent profiles.
Integrates with capability registry for node validation.
"""

import json
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import jsonschema


class AgentProfileRegistry:
    """
    Central registry for managing agent profiles with validation,
    versioning, and capability cross-checking.
    """

    def __init__(self, storage_path: str = "~/.hypersync/agents.json", 
                 schema_path: Optional[str] = None,
                 capability_registry: Optional[Any] = None):
        """
        Initialize the agent profile registry.

        Args:
            storage_path: Path to persistent storage file
            schema_path: Path to agent profile JSON schema
            capability_registry: Reference to capability registry for validation
        """
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.schema_path = schema_path
        self.capability_registry = capability_registry
        self.profiles: Dict[str, Dict] = {}
        self.schema: Optional[Dict] = None

        # Load schema if provided
        if self.schema_path and os.path.exists(self.schema_path):
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)

        # Load existing profiles
        self._load_profiles()

    def _load_profiles(self) -> None:
        """Load profiles from persistent storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.profiles = data.get('profiles', {})
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load profiles from {self.storage_path}: {e}")
                self.profiles = {}

    def _save_profiles(self) -> None:
        """Persist profiles to storage."""
        data = {
            'profiles': self.profiles,
            'last_updated': datetime.utcnow().isoformat() + 'Z'
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _validate_profile(self, profile: Dict) -> None:
        """
        Validate profile against JSON schema and business rules.

        Args:
            profile: Profile dictionary to validate

        Raises:
            jsonschema.ValidationError: If schema validation fails
            ValueError: If business rule validation fails
        """
        # Schema validation
        if self.schema:
            jsonschema.validate(instance=profile, schema=self.schema)

        # Business rule validation
        if 'nodes' in profile and self.capability_registry:
            for node_id in profile['nodes']:
                if not self.capability_registry.node_exists(node_id):
                    raise ValueError(f"Node {node_id} not found in capability registry")

        # Validate routing config matches strategy
        strategy = profile.get('routing_strategy')
        config = profile.get('routing_config', {})

        if strategy == 'priority_weighted' and 'weights' not in config:
            raise ValueError("priority_weighted strategy requires 'weights' in routing_config")

        if strategy == 'explicit_sequence' and 'sequence' not in config:
            raise ValueError("explicit_sequence strategy requires 'sequence' in routing_config")

    def _generate_agent_id(self, name: str) -> str:
        """Generate unique agent ID from name."""
        base_id = f"agent-{name}"
        if base_id not in self.profiles:
            return base_id

        # Add suffix if collision
        counter = 1
        while f"{base_id}-{counter}" in self.profiles:
            counter += 1
        return f"{base_id}-{counter}"

    def create_profile(self, profile_data: Dict) -> str:
        """
        Create a new agent profile.

        Args:
            profile_data: Profile configuration dictionary

        Returns:
            agent_id: Unique identifier for the created profile

        Raises:
            ValueError: If validation fails
        """
        # Generate agent_id if not provided
        if 'agent_id' not in profile_data:
            profile_data['agent_id'] = self._generate_agent_id(profile_data['name'])

        agent_id = profile_data['agent_id']

        # Check for duplicates
        if agent_id in self.profiles:
            raise ValueError(f"Agent profile {agent_id} already exists")

        # Set defaults
        if 'version' not in profile_data:
            profile_data['version'] = '1.0.0'

        # Initialize lifecycle
        now = datetime.utcnow().isoformat() + 'Z'
        if 'lifecycle' not in profile_data:
            profile_data['lifecycle'] = {}

        profile_data['lifecycle'].update({
            'state': profile_data['lifecycle'].get('state', 'draft'),
            'created_at': now,
            'updated_at': now
        })

        # Validate
        self._validate_profile(profile_data)

        # Store
        self.profiles[agent_id] = profile_data
        self._save_profiles()

        return agent_id

    def get_profile(self, agent_id: str) -> Optional[Dict]:
        """
        Retrieve an agent profile by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            Profile dictionary or None if not found
        """
        return self.profiles.get(agent_id)

    def update_profile(self, agent_id: str, updates: Dict) -> None:
        """
        Update an existing agent profile.

        Args:
            agent_id: Agent identifier
            updates: Dictionary of fields to update

        Raises:
            ValueError: If agent not found or validation fails
        """
        if agent_id not in self.profiles:
            raise ValueError(f"Agent profile {agent_id} not found")

        profile = self.profiles[agent_id].copy()
        profile.update(updates)

        # Update timestamp
        if 'lifecycle' not in profile:
            profile['lifecycle'] = {}
        profile['lifecycle']['updated_at'] = datetime.utcnow().isoformat() + 'Z'

        # Validate
        self._validate_profile(profile)

        # Store
        self.profiles[agent_id] = profile
        self._save_profiles()

    def delete_profile(self, agent_id: str) -> None:
        """
        Delete an agent profile.

        Args:
            agent_id: Agent identifier

        Raises:
            ValueError: If agent not found
        """
        if agent_id not in self.profiles:
            raise ValueError(f"Agent profile {agent_id} not found")

        del self.profiles[agent_id]
        self._save_profiles()

    def list_profiles(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        List all agent profiles with optional filtering.

        Args:
            filters: Optional filter criteria (e.g., {'lifecycle.state': 'active'})

        Returns:
            List of profile dictionaries
        """
        profiles = list(self.profiles.values())

        if not filters:
            return profiles

        # Apply filters
        filtered = []
        for profile in profiles:
            match = True
            for key, value in filters.items():
                # Support nested keys with dot notation
                parts = key.split('.')
                obj = profile
                for part in parts:
                    if part not in obj:
                        match = False
                        break
                    obj = obj[part]

                if not match or obj != value:
                    match = False
                    break

            if match:
                filtered.append(profile)

        return filtered

    def activate_profile(self, agent_id: str) -> None:
        """
        Activate an agent profile (change state to 'active').

        Args:
            agent_id: Agent identifier
        """
        self.update_profile(agent_id, {
            'lifecycle': {'state': 'active'}
        })

    def deprecate_profile(self, agent_id: str) -> None:
        """
        Deprecate an agent profile (change state to 'deprecated').

        Args:
            agent_id: Agent identifier
        """
        self.update_profile(agent_id, {
            'lifecycle': {'state': 'deprecated'}
        })

    def get_profile_nodes(self, agent_id: str) -> List[str]:
        """
        Get list of node IDs associated with an agent profile.

        Args:
            agent_id: Agent identifier

        Returns:
            List of node IDs
        """
        profile = self.get_profile(agent_id)
        if not profile:
            return []
        return profile.get('nodes', [])

    def validate_node_capabilities(self, agent_id: str) -> Dict[str, Any]:
        """
        Validate that all nodes in profile meet capability requirements.

        Args:
            agent_id: Agent identifier

        Returns:
            Validation report with status and details
        """
        profile = self.get_profile(agent_id)
        if not profile:
            return {'valid': False, 'error': 'Profile not found'}

        if not self.capability_registry:
            return {'valid': True, 'warning': 'No capability registry configured'}

        report = {
            'valid': True,
            'nodes': {},
            'errors': []
        }

        required_caps = profile.get('capabilities', {}).get('required', [])
        excluded_caps = profile.get('capabilities', {}).get('excluded', [])

        for node_id in profile.get('nodes', []):
            node_caps = self.capability_registry.get_node_capabilities(node_id)

            node_report = {
                'has_required': [],
                'missing_required': [],
                'has_excluded': []
            }

            # Check required capabilities
            for cap in required_caps:
                if cap in node_caps:
                    node_report['has_required'].append(cap)
                else:
                    node_report['missing_required'].append(cap)
                    report['valid'] = False
                    report['errors'].append(
                        f"Node {node_id} missing required capability: {cap}"
                    )

            # Check excluded capabilities
            for cap in excluded_caps:
                if cap in node_caps:
                    node_report['has_excluded'].append(cap)
                    report['valid'] = False
                    report['errors'].append(
                        f"Node {node_id} has excluded capability: {cap}"
                    )

            report['nodes'][node_id] = node_report

        return report
