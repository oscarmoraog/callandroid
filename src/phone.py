import re
import urllib.parse


def extract_phone_from_url(url: str) -> str:
    if not url:
        raise ValueError("URL vazia.")

    decoded = urllib.parse.unquote(url)

    m = re.match(r"^callandroid://(.+)$", decoded, re.IGNORECASE)
    if m:
        raw = m.group(1).strip().rstrip("/")
        if not raw:
            raise ValueError("Nenhum numero de telefone na URL.")
        return raw

    raise ValueError("Protocolo invalido. Use http://localhost:39527/call/NUMERO")


def normalize_phone(phone: str) -> str:
    cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "")
    return cleaned


def validate_phone(phone: str) -> bool:
    return bool(re.match(r"^\+?\d+$", phone))
