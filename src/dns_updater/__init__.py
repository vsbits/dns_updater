import logging
import sys
from .config import generate_config
from .core import update_dns, get_ip
from .cache import load_cache, create_cache


def main():
    CONFIG = generate_config()

    logging.basicConfig(
        level=logging.INFO,
        filename=CONFIG["LOGGING_FILE"],
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("Checking for IP changes")
    cache_file = CONFIG["CACHE_FILE"]

    # Get cached IP
    try:
        cache = load_cache(cache_file)
    except FileNotFoundError:
        logging.warning(
            f"Failed to locate cache file '{cache_file}'",
        )

        try:
            create_cache(cache_file)
        except Exception as e:
            logging.error(e, exc_info=True)
            sys.exit(1)
        logging.info("File successfully created")

    # Fetch Current IP
    try:
        current_ip = get_ip(CONFIG["IP_URL"])
    except (ConnectionError, ValueError) as e:
        logging.error(e)
        sys.exit(1)

    if cache.compare(current_ip, update=True):
        logging.info("IP unchanged")
        return

    logging.info(f"Current IP is {current_ip}")

    # Update to cloudflare DNS server
    try:
        update_dns(
            CONFIG["TOKEN"],
            current_ip,
            CONFIG["NAME"],
            CONFIG["PROXIED"],
            CONFIG["TYPE"],
            CONFIG["ZONE_ID"],
            CONFIG["ID"]
        )
    except Exception as e:
        if isinstance(e, ConnectionError):
            logging.error("Failed to authenticate to DNS server")
        else:
            logging.error("Unexpected error when updating DNS", exc_info=True)
        sys.exit(1)

    logging.info("DNS updated")

    # Cache current IP
    try:
        cache.save()
    except Exception:
        logging.error("Failed to update local cache")
        sys.exit(1)
    logging.info("Local cache updated")

    sys.exit(0)
