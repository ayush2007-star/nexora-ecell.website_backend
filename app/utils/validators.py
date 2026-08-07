import re


def validate_phone(phone):

    pattern = r"^[6-9]\d{9}$"

    return bool(
        re.match(pattern, phone)
    )


def validate_email(email):

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    return bool(
        re.match(pattern, email)
    )
