import requests
import re
import logging
import json
import sys
from dotenv import load_dotenv
from os import getenv


load_dotenv()
_LOGGING_FILE = getenv("LOGGING_FILE", "dns_updater.log")
_CACHE_FILE = getenv("CACHE_FILE", "dns_updater_cache")


logging.basicConfig(
    level=logging.INFO,
    filename=_LOGGING_FILE,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def dns_updater(
        ip_url: str,
        tk: str,
        name: str,
        proxied: bool,
        rec_type: str,
        zone: str,
        id: str
):
    logging.info("Checking for IP changes")

    # Get cached IP
    try:
        with open(_CACHE_FILE) as file:
            cached_ip = file.read().strip()
    except FileNotFoundError:
        logging.warning(
            f"Failed to locate cache file '{_CACHE_FILE}'",
        )
        cached_ip = None

        try:
            _create_cache_file()
        except Exception as e:
            logging.error(e, exc_info=True)
            sys.exit(1)
        logging.info("File successfully created")

    # Fetch Current IP
    try:
        current_ip = get_ip(ip_url)
    except (ConnectionError, ValueError) as e:
        logging.error(e)
        sys.exit(1)

    if current_ip == cached_ip:
        logging.info("IP unchanged")
        return

    logging.info(f"Current IP is {current_ip}")

    # Update to cloudflare DNS server
    try:
        update_dns(tk, current_ip, name, proxied, rec_type, zone, id)
    except Exception as e:
        if isinstance(e, ConnectionError):
            logging.error("Failed to authenticate to DNS server")
        else:
            logging.error("Unexpected error when updating DNS", exc_info=True)
        sys.exit(1)

    logging.info("DNS updated")

    # Cache current IP
    try:
        _update_cache(current_ip)
    except Exception:
        logging.error("Failed to update local cache")
        sys.exit(1)
    logging.info("Local cache updated")

    sys.exit(0)


def _is_ip(content: str) -> bool:
    """
Checks if a string is a valid IP without extra characters

content: string to be checked
"""
    if "\n" in content:
        return False

    ip_pattern = re.compile("^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$")
    return bool(re.match(ip_pattern, content))


def get_ip(url: str) -> str:
    """
Gets current external IP using a get request to an API (it must return only
the IP value in the response body)

url: API url
"""

    r = requests.get(url)

    if r.status_code != 200:
        raise ConnectionError("Error connecting to server")

    ip = r.text.strip()

    if _is_ip(ip):
        return ip

    raise ValueError("Response from server was not an IP")


def _create_cache_file(cache_file: str = _CACHE_FILE):
    """
Creates a file to store the IP value

cache_file: filepath
"""
    with open(cache_file, "x"):
        pass


def _update_cache(new_ip: str, cache_file: str = _CACHE_FILE):
    """
Saves the `new_ip` value to cache

new_ip: IP value to be stored
cache_file: path_
"""
    with open(cache_file, "w") as file:
        file.write(new_ip)


def update_dns(
    tk: str,
    new_ip: str,
    name: str,
    proxied: bool,
    rec_type: str,
    zone: str,
    id: str,
):
    """
Updates the Cloudflare DNS record with the new IP

tk: API token
new_ip: IP address
name: record name,
proxied: proxied by Cloudflare,
rec_type: record type,
zone: DNS zone ID
id: record ID
"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records/{id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {tk}"
    }
    payload = {
        "content": new_ip,
        "name": name,
        "proxied": proxied,
        "type": rec_type
    }

    r = requests.put(url, json=payload, headers=headers)

    if r.status_code != 200:
        raise ConnectionError

    json_response = json.loads(r.text)
    if not json_response.get("success"):
        errors = json_response.get("errors")
        raise ValueError(json.dumps(errors))


class ConnectionError(Exception):
    pass
