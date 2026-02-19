#!/usr/bin/env python3
"""
HyperSync Tier Filter Tool
Extract and validate Core tier files from full HyperSync project
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
import re


class TierFilter:
    """Main tier filtering and extraction logic"""
    
    CORE_TIER = "core"
    VALID_TIERS = ["core", "basic", "pro", "advanced", "enterprise"]
    
    def __init__(self, source_dir: Path, config_dir: Path):
        self.source_dir = Path(source_dir)
        self.config_dir = Path(config_dir)
        self.tier_rules = self._load_tier_rules()
        self.component_mapping = self._load_component_mapping()
        self.errors = []
        self.warnings = []
        
    def _load_tier_rules(self) -> Dict[str, Any]:
        """Load tier boundary rules from config"""
        rules_file = self.config_dir / "tier_rules.json"
        if rules_file.exists():
            with open(rules_file, 'r') as f:
                return json.load(f)
        return self._default_tier_rules()
    
    def _load_component_mapping(self) -> Dict[str, Any]:
        """Load component tier assignments from config"""
        mapping_file = self.config_dir / "component_mapping.json"
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                return json.load(f)
        return self._default_component_mapping()
    
    def _default_tier_rules(self) -> Dict[str, Any]:
        """Default tier filtering rules"""
        return {
            "core": {
                "complexity": ["O(n)", "O(1)", "O(log n)"],
                "exclude_patterns": [
                    "*/basic/*", "*/pro/*", "*/advanced/*", "*/enterprise/*",
                    "*_ml_*", "*_quantum_*", "*_distributed_*"
                ],
                "include_patterns": [
                    "*/core/*", "*_core.*", "*_efficient_*"
                ],
                "forbidden_keywords": [
                    "machine_learning", "neural_network", "quantum",
                    "distributed_consensus", "blockchain", "enterprise_"
                ]
            }
        }
    
    def _default_component_mapping(self) -> Dict[str, Any]:
        """Default component tier assignments"""
        return {
            "agua": {"tier": "partial", "core_subdirs": ["specs/core", "reference/core", "docs/core"]},
            "pct": {"tier": "partial", "core_subdirs": ["specs/core", "reference/core", "docs/core"]},
            "sdl": {"tier": "partial", "core_subdirs": ["specs/core", "reference/basic", "docs/core"]},
            "hvs-nvm": {"tier": "full"},
            "vnes": {"tier": "full"},
            "mom": {"tier": "none"},
            "haw": {"tier": "none"},
            "ascif": {"tier": "none"},
            "mxfy": {"tier": "none"}
        }
    
    def filter_and_export(self, output_dir: Path, target_tier: str = "core", validate: bool = True) -> bool:
        """Filter and export files for target tier"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[TierFilter] Filtering {target_tier} tier from {self.source_dir}")
        print(f"[TierFilter] Output directory: {output_dir}")
        
        self._export_specifications(output_dir, target_tier)
        self._export_components(output_dir, target_tier)
        self._export_tools(output_dir, target_tier)
        self._export_workspace(output_dir, target_tier)
        self._export_shared(output_dir, target_tier)
        self._export_docs(output_dir, target_tier)
        
        if validate:
            print(f"\n[TierFilter] Validating {target_tier} tier export...")
            is_valid = self.validate_tier_export(output_dir, target_tier)
            if not is_valid:
                print(f"[TierFilter] ❌ Validation failed with {len(self.errors)} errors")
                for error in self.errors:
                    print(f"  ERROR: {error}")
                return False
        
        print(f"\n[TierFilter] ✅ Export complete: {output_dir}")
        if self.warnings:
            print(f"[TierFilter] ⚠️  {len(self.warnings)} warnings:")
            for warning in self.warnings[:10]:
                print(f"  WARNING: {warning}")
        
        return True
    
    def _export_specifications(self, output_dir: Path, tier: str):
        """Export specifications for target tier"""
        print("\n[Specifications] Exporting...")
        specs_src = self.source_dir / "specifications" / tier
        specs_dst = output_dir / "specifications" / tier
        
        if specs_src.exists():
            shutil.copytree(specs_src, specs_dst, dirs_exist_ok=True)
            print(f"  ✓ Copied {tier} specifications")
        
        for doc in ["CORE_TIER_PROMOTIONS.md", "HYPERSYNC_COMPLETE_TIER_HIERARCHY.md"]:
            doc_src = self.source_dir / "specifications" / doc
            if doc_src.exists():
                shutil.copy2(doc_src, output_dir / "specifications" / doc)
                print(f"  ✓ Copied {doc}")
    
    def _export_components(self, output_dir: Path, tier: str):
        """Export components for target tier"""
        print("\n[Components] Exporting...")
        components_src = self.source_dir / "components" / "production"
        components_dst = output_dir / "components" / "production"
        components_dst.mkdir(parents=True, exist_ok=True)
        
        for component_name, config in self.component_mapping.items():
            comp_tier = config.get("tier")
            
            if comp_tier == "none":
                print(f"  ⊗ Skipping {component_name} (not in {tier} tier)")
                continue
            
            comp_src = components_src / component_name
            comp_dst = components_dst / component_name
            
            if not comp_src.exists():
                self.warnings.append(f"Component {component_name} not found at {comp_src}")
                continue
            
            if comp_tier == "full":
                shutil.copytree(comp_src, comp_dst, dirs_exist_ok=True)
                print(f"  ✓ Copied {component_name} (full)")
            
            elif comp_tier == "partial":
                comp_dst.mkdir(parents=True, exist_ok=True)
                core_subdirs = config.get("core_subdirs", [])
                
                for subdir in core_subdirs:
                    subdir_src = comp_src / subdir
                    subdir_dst = comp_dst / subdir
                    if subdir_src.exists():
                        shutil.copytree(subdir_src, subdir_dst, dirs_exist_ok=True)
                        print(f"  ✓ Copied {component_name}/{subdir}")
                
                meta_src = comp_src / "meta.json"
                if meta_src.exists():
                    shutil.copy2(meta_src, comp_dst / "meta.json")
                    print(f"  ✓ Copied {component_name}/meta.json")
        
        template_src = self.source_dir / "components" / "experimental" / "_template"
        template_dst = output_dir / "components" / "experimental" / "_template"
        if template_src.exists():
            shutil.copytree(template_src, template_dst, dirs_exist_ok=True)
            print(f"  ✓ Copied experimental template")
    
    def _export_tools(self, output_dir: Path, tier: str):
        """Export tools for target tier"""
        print("\n[Tools] Exporting...")
        tools_src = self.source_dir / "tools"
        tools_dst = output_dir / "tools"
        
        core_tools = ["component-creator", "live-analyzer", "stunir", "validators", "tier-filter"]
        
        for tool in core_tools:
            tool_src = tools_src / tool
            tool_dst = tools_dst / tool
            if tool_src.exists():
                shutil.copytree(tool_src, tool_dst, dirs_exist_ok=True)
                print(f"  ✓ Copied {tool}")
        
        index_src = tools_src / "index.json"
        if index_src.exists():
            shutil.copy2(index_src, tools_dst / "index.json")
            print(f"  ✓ Copied tools/index.json")
    
    def _export_workspace(self, output_dir: Path, tier: str):
        """Export workspace structure for target tier"""
        print("\n[Workspace] Exporting...")
        workspace_src = self.source_dir / "workspace"
        workspace_dst = output_dir / "workspace"
        
        if workspace_src.exists():
            shutil.copytree(workspace_src, workspace_dst, dirs_exist_ok=True)
            print(f"  ✓ Copied workspace")
    
    def _export_shared(self, output_dir: Path, tier: str):
        """Export shared resources for target tier"""
        print("\n[Shared] Exporting...")
        shared_src = self.source_dir / "shared"
        shared_dst = output_dir / "shared"
        
        for subdir in ["protocols", "types"]:
            subdir_src = shared_src / subdir
            subdir_dst = shared_dst / subdir
            if subdir_src.exists():
                shutil.copytree(subdir_src, subdir_dst, dirs_exist_ok=True)
                print(f"  ✓ Copied shared/{subdir}")
        
        for partial_subdir in ["specs", "libraries"]:
            core_src = shared_src / partial_subdir / tier
            core_dst = shared_dst / partial_subdir / tier
            if core_src.exists():
                shutil.copytree(core_src, core_dst, dirs_exist_ok=True)
                print(f"  ✓ Copied shared/{partial_subdir}/{tier}")
    
    def _export_docs(self, output_dir: Path, tier: str):
        """Export documentation for target tier"""
        print("\n[Documentation] Exporting...")
        docs_src = self.source_dir / "docs" / tier
        docs_dst = output_dir / "docs" / tier
        
        if docs_src.exists():
            shutil.copytree(docs_src, docs_dst, dirs_exist_ok=True)
            print(f"  ✓ Copied docs/{tier}")
    
    def validate_tier_export(self, export_dir: Path, tier: str) -> bool:
        """Validate that export contains only target tier files"""
        print(f"\n[Validation] Checking {tier} tier boundaries...")
        is_valid = True
        
        rules = self.tier_rules.get(tier, {})
        exclude_patterns = rules.get("exclude_patterns", [])
        forbidden_keywords = rules.get("forbidden_keywords", [])
        
        for root, dirs, files in os.walk(export_dir):
            root_path = Path(root)
            
            for exclude_pattern in exclude_patterns:
                if self._matches_pattern(root_path, exclude_pattern):
                    self.errors.append(f"Found excluded path: {root_path}")
                    is_valid = False
            
            for file in files:
                file_path = root_path / file
                
                if file.endswith('.json'):
                    is_valid = self._validate_json_file(file_path, tier, forbidden_keywords) and is_valid
        
        return is_valid
    
    def _validate_json_file(self, file_path: Path, tier: str, forbidden_keywords: List[str]) -> bool:
        """Validate JSON file for tier compliance"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = json.loads(content)
            
            if "metadata" in data and "tier" in data["metadata"]:
                file_tier = data["metadata"]["tier"]
                if file_tier != tier:
                    self.errors.append(f"File {file_path} has tier '{file_tier}', expected '{tier}'")
                    return False
            
            for keyword in forbidden_keywords:
                if keyword in content.lower():
                    self.errors.append(f"File {file_path} contains forbidden keyword: {keyword}")
                    return False
            
            return True
        
        except Exception as e:
            self.warnings.append(f"Could not validate {file_path}: {e}")
            return True
    
    def _matches_pattern(self, path: Path, pattern: str) -> bool:
        """Check if path matches exclude pattern"""
        path_str = str(path)
        pattern_regex = pattern.replace("*", ".*").replace("/", os.sep)
        return re.search(pattern_regex, path_str) is not None
    
    def generate_catalog(self, export_dir: Path, output_file: Path):
        """Generate catalog of Core tier operations"""
        print(f"\n[Catalog] Generating {output_file}...")
        
        catalog = {
            "core_tier": {
                "components": {},
                "specifications": {},
                "total_operations": 0
            }
        }
        
        components_dir = export_dir / "components" / "production"
        if components_dir.exists():
            for comp_dir in components_dir.iterdir():
                if comp_dir.is_dir():
                    meta_file = comp_dir / "meta.json"
                    if meta_file.exists():
                        with open(meta_file, 'r') as f:
                            meta = json.load(f)
                            catalog["core_tier"]["components"][comp_dir.name] = meta
        
        with open(output_file, 'w') as f:
            json.dump(catalog, f, indent=2)
        
        print(f"  ✓ Catalog written to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="HyperSync Tier Filter Tool")
    parser.add_argument("--source", required=True, help="Source directory (build/current)")
    parser.add_argument("--output", required=True, help="Output directory for filtered tier")
    parser.add_argument("--tier", default="core", choices=["core", "basic", "pro", "advanced", "enterprise"])
    parser.add_argument("--validate", action="store_true", help="Validate tier boundaries")
    parser.add_argument("--verify-tier", help="Verify existing export is tier-compliant")
    parser.add_argument("--generate-catalog", action="store_true", help="Generate operation catalog")
    parser.add_argument("--output-catalog", help="Catalog output file")
    
    args = parser.parse_args()
    
    source_dir = Path(args.source)
    output_dir = Path(args.output)
    config_dir = Path(__file__).parent / "config"
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        sys.exit(1)
    
    tier_filter = TierFilter(source_dir, config_dir)
    
    if args.verify_tier:
        print(f"Verifying tier compliance for: {args.verify_tier}")
        is_valid = tier_filter.validate_tier_export(Path(args.verify_tier), args.tier)
        sys.exit(0 if is_valid else 1)
    
    if args.generate_catalog:
        catalog_file = Path(args.output_catalog) if args.output_catalog else output_dir / "CORE_TIER_CATALOG.json"
        tier_filter.generate_catalog(output_dir, catalog_file)
        sys.exit(0)
    
    success = tier_filter.filter_and_export(output_dir, args.tier, args.validate)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
