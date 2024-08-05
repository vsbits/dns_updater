import json
import requests
import re


def is_valid_ip(content: str) -> bool:
    """
Checks if a string is a valid IP without extra characters

content: string to be checked
"""
    if "\n" in content:
        return False

    ip_pattern = re.compile("^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$")
    matches = ip_pattern.match(content)

    if matches and all(
        len(v) == 1 or not v.startswith("0") for v in content.split(".")
    ):
        return bool(matches)
    return False


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

    if is_valid_ip(ip):
        return ip

    raise ValueError("Response from server was not a valid IP")


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
