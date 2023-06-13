from dotenv import load_dotenv
from os import getenv


def _required_getenv(key: str) -> str:
    """
Gets environment variable. Raises error if not found

key: ENV VARIABLE key
"""
    value = getenv(key)
    if value is None:
        raise ValueError(f"The ENV VARIABLE {key} must be defined")
    return value


load_dotenv()


CONFIG = {
    "LOGGING_FILE": getenv("LOGGING_FILE", "dns_updater.log"),
    "CACHE_FILE": getenv("CACHE_FILE", "dns_updater_cache"),
    "IP_URL": _required_getenv("IP_SERVICE_URL"),
    "TOKEN": _required_getenv("TOKEN"),
    "ZONE_ID": _required_getenv("ZONE_ID"),
    "ID": _required_getenv("ID"),
    "NAME": _required_getenv("NAME"),
    "TYPE": _required_getenv("TYPE"),
    "PROXIED": bool(getenv("PROXIED"))
}
