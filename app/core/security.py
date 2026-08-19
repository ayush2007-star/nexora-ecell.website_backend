import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password securely using bcrypt.
    """
    if isinstance(password, str):
        pwd_bytes = password.encode("utf-8")
    else:
        pwd_bytes = password

    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its bcrypt hash.
    """
    if not plain_password or not hashed_password:
        return False

    try:
        if isinstance(plain_password, str):
            plain_bytes = plain_password.encode("utf-8")
        else:
            plain_bytes = plain_password

        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode("utf-8")
        else:
            hashed_bytes = hashed_password

        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False