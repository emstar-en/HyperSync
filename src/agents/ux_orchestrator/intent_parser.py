
import os
import re
from typing import List, Dict, Optional

class Playbook:
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content
        self.trigger_keywords = self._extract_trigger_keywords()

    def _extract_trigger_keywords(self) -> List[str]:
        # Heuristic: Look for "Trigger" section and extract nouns/verbs
        # For now, we'll just use the filename as a strong hint
        return [self.name.replace('_', ' '), "create", "add", "new"]

class IntentParser:
    def __init__(self, playbooks_dir: str):
        self.playbooks: Dict[str, Playbook] = {}
        self._load_playbooks(playbooks_dir)

    def _load_playbooks(self, directory: str):
        if not os.path.exists(directory):
            return
        for filename in os.listdir(directory):
            if filename.endswith(".md"):
                with open(os.path.join(directory, filename), 'r') as f:
                    name = filename.replace('.md', '')
                    self.playbooks[name] = Playbook(name, f.read())

    def parse(self, user_input: str) -> Optional[Playbook]:
        """
        Determines which playbook matches the user's intent.
        """
        user_input = user_input.lower()

        # Simple keyword matching for now
        if "help" in user_input or "what can you do" in user_input:
            return self.playbooks.get("help")
        
        if "extension" in user_input or "capability" in user_input:
            return self.playbooks.get("create_extension")

        return None
