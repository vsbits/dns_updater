from os import getenv
from .dns_updater import dns_updater


def _required_getenv(key: str) -> str:
    """
Gets environment variable. Raises error if not found

key: ENV VARIABLE key
"""
    value = getenv(key)
    if value is None:
        raise ValueError(f"The ENV VARIABLE {key} must be defined")
    return value


def main():
    ip_url = _required_getenv("IP_SERVICE_URL")
    token = _required_getenv("TOKEN")
    zone_id = _required_getenv("ZONE_ID")
    id = _required_getenv("ID")
    name = _required_getenv("NAME")
    rec_type = _required_getenv("TYPE")
    proxied = bool(getenv("PROXIED"))
    dns_updater(ip_url, token, name, proxied, rec_type, zone_id, id)
