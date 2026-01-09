
from typing import Dict, Any

class FormatDetector:
    def detect(self, data: Any, filename: str = "") -> Dict[str, Any]:
        """
        Analyzes data to determine format metadata.
        """
        metadata = {
            "mime": "application/octet-stream",
            "extension": "",
            "size": 0
        }

        # 1. Extension check
        if filename:
            ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
            metadata["extension"] = ext
            if ext == ".csv":
                metadata["mime"] = "text/csv"
            elif ext == ".json":
                metadata["mime"] = "application/json"
            elif ext in [".jpg", ".png"]:
                metadata["mime"] = f"image/{ext[1:]}"

        # 2. Magic Byte check (Stub)
        if isinstance(data, bytes):
            metadata["size"] = len(data)
            if data.startswith(b'PNG

'):
                metadata["mime"] = "image/png"
                metadata["extension"] = ".png"

        return metadata
