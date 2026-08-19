from typing import Any

from app.core.jwt import decode_token


def verify_token(token: str) -> dict[str, Any] | None:
    """
    Verify and decode an access token.

    This function is kept as the public verification helper so
    existing code can continue importing verify_token from
    app.utils.jwt.
    """

    if not token:
        return None

    return decode_token(token)