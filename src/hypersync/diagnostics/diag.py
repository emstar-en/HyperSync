from __future__ import annotations
from pathlib import Path
import json

class Diagnostics:
    def __init__(self, root: Path):
        self.root = root

    def profiles(self):
        pdir = self.root / 'refs' / 'diagnostics' / 'profiles'
        return sorted(pdir.glob('*.json')) if pdir.exists() else []

    def rules(self):
        rdir = self.root / 'refs' / 'diagnostics' / 'rules'
        return sorted(rdir.glob('*.json')) if rdir.exists() else []
