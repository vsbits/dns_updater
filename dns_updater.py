import requests
import re
import logging
import json
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


def main(
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
            return
        logging.info("File successfully created")

    # Fetch Current IP
    try:
        current_ip = get_ip(ip_url)
    except (ConnectionError, ValueError) as e:
        logging.error(e)
        return

    if current_ip == cached_ip:
        logging.info("IP unchanged")
        return

    logging.info(f"Current IP is {current_ip}")

    # Update to cloudflare DNS server
    try:
        update_dns(tk, current_ip, name, proxied, rec_type, zone, id)
    except ConnectionError:
        logging.error("Failed to authenticate to DNS server")
    except Exception:
        logging.error("Unexpected error when updating DNS", exc_info=True)

    logging.info("DNS updated")

    # Cache current IP
    try:
        _update_cache(current_ip)
    except Exception:
        logging.error("Failed to update local cache")
    logging.info("Local cache updated")



def get_ip(url: str) -> str:
    """
Gets current external IP using a get request to an API (it must return only
the IP value in the response body)

url: API url
"""
    ip_pattern = re.compile("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}")

    r = requests.get(url)

    if r.status_code != 200:
        raise ConnectionError("Error connecting to server")

    ip = r.text.strip()
    if re.match(ip_pattern, ip) is None:
        raise ValueError("Response from server was not an IP")
    
    return ip


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


def _required_getenv(key: str) -> str:
    """
Gets environment variable. Raises error if not found

key: ENV VARIABLE key
"""
    value = getenv(key)
    if value is None:
        raise ValueError(f"The ENV VARIABLE {key} must be defined")
    return value


if __name__ == "__main__":
    ip_url = _required_getenv("IP_SERVICE_URL")
    token = _required_getenv("TOKEN")
    zone_id = _required_getenv("ZONE_ID")
    id = _required_getenv("ID")
    name = _required_getenv("NAME")
    rec_type = _required_getenv("TYPE")
    proxied = bool(getenv("PROXIED"))
    main(ip_url, token, name, proxied, rec_type, zone_id, id)
