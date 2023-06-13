# DNS updater

Script to update a DNS record on Cloudflare.

## Instalation

Just clone this repository and run `pip install`:

```
git clone https://github.com/vs-araujo/dns_updater && \
cd dns_updater && \
pip install .
```

After installation, you should have access to the `update_dns` command through
your shell.

The script uses the following environment variables, some of them are required for it to run.
You can either `export` them or use a `.env` file:

### `LOGGING_FILE` [Optional]
Path to the script log file. Default is `dns_updater.log`.

### `CACHE_FILE` [Optional]
Path to the cache of last IP value successfully updated. Dafault is `dns_updater_cache`.

### `IP_SERVICE_URL` [Required]
API URL to get the current IP. The API must return only the IP value in the Response body.

### `TOKEN` [Required]
Cloudflare API token

### `ZONE_ID` [Required]
ID of the record zone

### `ID` [Required]
Record ID

### `NAME` [Required]
Record name

### `TYPE` [Required]
Record type

### `PROXIED` [Optional]
If is proxied by Cloudflare
