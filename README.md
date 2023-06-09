# DNS updater

Script to update a DNS record on Cloudflare.

## ENV VARIABLES
The script uses environment variables. Some of them are required for it to run.

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
