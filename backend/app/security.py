from typing import Optional
import hmac

from fastapi import Header, HTTPException, status

from app.config import API_KEY, API_KEY_SERVIDOR


def require_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> None:
    valid_keys = (API_KEY, API_KEY_SERVIDOR)

    if not x_api_key or not any(
        key and hmac.compare_digest(x_api_key, key)
        for key in valid_keys
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API invalida ou ausente",
        )
