
from typing import List, Dict, Any
from .base import BaseUIR

class USTAB(BaseUIR):
    """Universal Tabular Data"""
    # Payload structure: {"columns": [...], "data": [[...], [...]]}
    pass

class UIMG(BaseUIR):
    """Universal Image Data"""
    # Payload structure: {"format": "png", "dimensions": (w, h), "bytes": b"..."}
    pass

class UGEO(BaseUIR):
    """Universal Geometric Data"""
    # Payload structure: {"coordinates": [...], "space": "poincare_disk"}
    pass
