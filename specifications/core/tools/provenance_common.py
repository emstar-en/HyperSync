# Common provenance helpers
import hashlib, json, base64, time


def sha256_b64(data: bytes) -> str:
    return 'sha256-' + base64.b64encode(hashlib.sha256(data).digest()).decode()


def write_receipt(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

