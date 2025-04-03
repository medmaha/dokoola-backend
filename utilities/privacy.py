import re


def mask_email(email: str) -> str:
    if not email:
        return None
    return email[0:1] + "****@" + email.split("@", 1)[1]


def mask_phone_number(phone_number: str) -> str:
    if not phone_number:
        return None
    return re.sub(r".(?=.{4})", "*", phone_number)
