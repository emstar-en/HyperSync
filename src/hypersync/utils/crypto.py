from __future__ import annotations
import hmac, hashlib, base64

def hmac_b64(secret: str, message: str) -> str:
    sig = hmac.new(secret.encode('utf-8'), msg=message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode('ascii')
