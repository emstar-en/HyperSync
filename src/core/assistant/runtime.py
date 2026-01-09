"""
HyperSync Initialization Assistant - Runtime

Minimal, offline runtime that uses NVM+rules for retrieval and response generation.
No external LLM required - operates entirely on local knowledge packs.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AssistantRuntime:
    """
    Initialization Assistant runtime with rules+retrieval engine.

    Uses local NVM knowledge packs for offline operation.
    Provides conversational interface for HyperSync setup and operations.
    """

    def __init__(self, manifest: str = "iam/model.manifest.json"):
        """
        Initialize the assistant runtime.

        Args:
            manifest: Path to IAM manifest file
        """
        self.manifest_path = Path(manifest)
        self.manifest = self._load_manifest()

        # Import tools bridge
        from hypersync.assistant import tools_bridge
        self.tools = tools_bridge

        # Load NVM knowledge packs
        packs = self.manifest["runner"]["config"]["nvm_packs"]
        self.nvm_docs = self._load_jsonl(packs[0]) if packs else []

        logger.info(f"Initialized IAM runtime with {len(self.nvm_docs)} knowledge entries")

    def _load_manifest(self) -> Dict[str, Any]:
        """Load and validate IAM manifest"""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")

        try:
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid manifest JSON: {e}")

    def _load_jsonl(self, path: str) -> List[Dict[str, Any]]:
        """Load JSONL knowledge pack"""
        docs = []
        p = Path(path)

        if not p.exists():
            logger.warning(f"Knowledge pack not found: {path}")
            return docs

        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                docs.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        return docs

    def respond(self, text: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate response to user message using rules+retrieval.

        Args:
            text: User message
            ctx: Conversation context (e.g., {"ld_id": "...", "session_id": "..."})

        Returns:
            {
                "reply": str,
                "actions": List[Dict],
                "suggestions": List[str]
            }
        """
        t = text.strip().lower()

        # Rule 1: Setup/Initialization
        if self._matches_setup(t):
            return self._handle_setup(ctx)

        # Rule 2: Catalog/Register Models
        if self._matches_catalog(t):
            return self._handle_catalog(ctx)

        # Rule 3: Compose Agent
        if self._matches_compose(t):
            return self._handle_compose(text, ctx)

        # Rule 4: Compute Route
        if self._matches_route(t):
            return self._handle_route(text, ctx)

        # Rule 5: Status/Summary
        if self._matches_status(t):
            return self._handle_status(ctx)

        # Fallback: Retrieval from NVM
        answer = self._retrieve_knowledge(t)
        if answer:
            return {
                "reply": answer,
                "actions": [],
                "suggestions": self._get_suggestions()
            }

        # Default: Offer help
        return {
            "reply": self._get_help_message(),
            "actions": [],
            "suggestions": self._get_suggestions()
        }

    # ========================================================================
    # Intent Matching
    # ========================================================================

    def _matches_setup(self, text: str) -> bool:
        """Check if text matches setup intent"""
        keywords = ["set me up", "initialize", "get started", "first time", "setup"]
        return any(kw in text for kw in keywords) or (
            "create" in text and any(w in text for w in ["ld", "domain", "workspace"])
        )

    def _matches_catalog(self, text: str) -> bool:
        """Check if text matches catalog intent"""
        keywords = ["catalog", "scan", "register models", "find models", "list models"]
        return any(kw in text for kw in keywords)

    def _matches_compose(self, text: str) -> bool:
        """Check if text matches compose intent"""
        return "compose" in text and "agent" in text

    def _matches_route(self, text: str) -> bool:
        """Check if text matches route intent"""
        return "route" in text and " to " in text

    def _matches_status(self, text: str) -> bool:
        """Check if text matches status intent"""
        keywords = ["status", "summary", "show me", "what do i have", "list"]
        return any(kw in text for kw in keywords)

    # ========================================================================
    # Intent Handlers
    # ========================================================================

    def _handle_setup(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Handle setup/initialization request"""
        try:
            res = self.tools.create_ld({
                "name": "secure-workspace",
                "security_level": "isolated"
            })

            ctx["ld_id"] = res["ld_id"]

            return {
                "reply": f"✓ Created secure Lorentzian Domain: {res['ld_id']}\n"
                        f"  Name: {res['name']}\n"
                        f"  Security: isolated\n\n"
                        f"Next, I can scan for local models in .hypersync/models/ and register them.\n"
                        f"Would you like me to catalog your models?",
                "actions": [{"create_ld": res}],
                "suggestions": ["Catalog my models", "Show me the status"]
            }
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return {
                "reply": f"Setup failed: {str(e)}\n\nPlease check the logs for details.",
                "actions": [],
                "suggestions": ["Try again", "Show me the status"]
            }

    def _handle_catalog(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Handle catalog/register models request"""
        try:
            cat = self.tools.catalog_models({})

            if cat["count"] == 0:
                return {
                    "reply": "No model descriptors found in .hypersync/models/\n\n"
                            "To add models:\n"
                            "1. Copy model descriptor JSON files to .hypersync/models/\n"
                            "2. Ask me to \"catalog models\" again\n\n"
                            "I can provide example descriptors if you'd like!",
                    "actions": [],
                    "suggestions": ["Show me example descriptors", "Create a domain"]
                }

            # Ensure we have an LD
            ld_id = ctx.get("ld_id")
            if not ld_id:
                ld = self.tools.create_ld({"name": "secure-workspace"})
                ld_id = ld["ld_id"]
                ctx["ld_id"] = ld_id

            # Register each model
            registered = []
            for m in cat["models"]:
                name = m.get("name")
                if name:
                    self.tools.register_node({
                        "ld_id": ld_id,
                        "node_id": name,
                        "address_type": m.get("type", "model")
                    })
                    registered.append(name)

            model_list = "\n".join(f"  • {name}" for name in registered)

            return {
                "reply": f"✓ Found {cat['count']} model(s) in .hypersync/models/\n"
                        f"✓ Registered {len(registered)} node(s) in LD {ld_id}:\n"
                        f"{model_list}\n\n"
                        f"Next steps:\n"
                        f"• Compute a route: \"Route {registered[0]} to {registered[1]}\"\n"
                        f"• Compose an agent: \"Compose agent from {registered[0]} and {registered[1]}\"",
                "actions": [{"catalog": cat, "ld_id": ld_id}],
                "suggestions": [
                    f"Route {registered[0]} to {registered[1]}" if len(registered) >= 2 else "Show status",
                    "Compose an agent"
                ]
            }
        except Exception as e:
            logger.error(f"Catalog failed: {e}")
            return {
                "reply": f"Catalog failed: {str(e)}",
                "actions": [],
                "suggestions": ["Try again", "Show me the status"]
            }

    def _handle_compose(self, text: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent composition request"""
        try:
            # Extract member names from quotes
            members = re.findall(r'"([^"]+)"', text)
            if not members:
                members = re.findall(r"'([^']+)'", text)

            if not members:
                return {
                    "reply": "Please specify member models in quotes.\n"
                            "Example: \"Compose agent from \\"model-a\\" and \\"model-b\\"\"",
                    "actions": [],
                    "suggestions": ["Show me my models", "Show status"]
                }

            res = self.tools.compose_agent({
                "name": "network-operator",
                "capabilities": ["route", "orchestrate"],
                "members": members,
                "ld_id": ctx.get("ld_id")
            })

            return {
                "reply": f"✓ Composed agent: {res['agent_id']}\n"
                        f"  Members: {', '.join(members)}\n"
                        f"  Domain: {res['ld_id']}\n\n"
                        f"The agent is now registered and ready to use!",
                "actions": [{"compose_agent": res}],
                "suggestions": ["Show status", "Compute a route"]
            }
        except Exception as e:
            logger.error(f"Compose failed: {e}")
            return {
                "reply": f"Composition failed: {str(e)}",
                "actions": [],
                "suggestions": ["Try again", "Show me my models"]
            }

    def _handle_route(self, text: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Handle route computation request"""
        try:
            # Extract src and dst from "route X to Y"
            match = re.search(r"route\s+([\w-]+)\s+to\s+([\w-]+)", text.lower())
            if not match:
                return {
                    "reply": "Please specify source and destination.\n"
                            "Example: \"Route model-a to model-b\"",
                    "actions": [],
                    "suggestions": ["Show me my models", "Show status"]
                }

            src, dst = match.groups()

            res = self.tools.compute_route({"src": src, "dst": dst})

            path_str = " → ".join(res["path"])

            return {
                "reply": f"✓ Route computed:\n  {path_str}\n\n"
                        f"Hops: {len(res['path']) - 1}",
                "actions": [{"route": res}],
                "suggestions": ["Compute another route", "Show status"]
            }
        except Exception as e:
            logger.error(f"Route computation failed: {e}")
            return {
                "reply": f"Route computation failed: {str(e)}\n\n"
                        f"Make sure both nodes are registered.",
                "actions": [],
                "suggestions": ["Show me my models", "Catalog models"]
            }

    def _handle_status(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status/summary request"""
        try:
            res = self.tools.status_summary({})

            if not res["domains"]:
                return {
                    "reply": "No domains found. Let me set you up!",
                    "actions": [],
                    "suggestions": ["Set me up", "Create a domain"]
                }

            domain_list = "\n".join(
                f"  • {d['name']} ({d['ld_id']}): {d['node_count']} nodes"
                for d in res["domains"]
            )

            return {
                "reply": f"📊 HyperSync Status:\n\n"
                        f"Domains ({len(res['domains'])}):\n{domain_list}\n\n"
                        f"Total Nodes: {res['total_nodes']}\n"
                        f"Total Agents: {res['total_agents']}",
                "actions": [{"status": res}],
                "suggestions": ["Catalog models", "Compose an agent"]
            }
        except Exception as e:
            logger.error(f"Status failed: {e}")
            return {
                "reply": f"Status check failed: {str(e)}",
                "actions": [],
                "suggestions": ["Try again"]
            }

    # ========================================================================
    # Knowledge Retrieval
    # ========================================================================

    def _retrieve_knowledge(self, query: str) -> Optional[str]:
        """Retrieve knowledge from NVM using simple lexical matching"""
        q_terms = set(query.split())
        best = None
        best_score = 0

        for doc in self.nvm_docs:
            # Combine title, body, and tags for matching
            text = (
                doc.get("title", "") + " " +
                doc.get("body", "") + " " +
                " ".join(doc.get("tags", []))
            ).lower()

            terms = set(text.split())
            score = len(q_terms & terms)

            if score > best_score:
                best = doc
                best_score = score

        if best and best_score > 0:
            return f"{best.get('title', '')}\n\n{best.get('body', '')}"

        return None

    def _get_help_message(self) -> str:
        """Get default help message"""
        return (
            "I'm your HyperSync Initialization Assistant! I can help you:\n\n"
            "• Create secure Lorentzian Domains (workspaces)\n"
            "• Register your local AI models as network nodes\n"
            "• Compute routes between models\n"
            "• Compose multi-model agents\n\n"
            "What would you like to do?"
        )

    def _get_suggestions(self) -> List[str]:
        """Get default suggestions"""
        return [
            "Set me up",
            "Catalog my models",
            "Show me the status"
        ]
