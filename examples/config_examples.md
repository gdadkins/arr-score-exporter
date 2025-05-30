# Configuration Examples

This file shows various ways you might configure the connection settings in `export_radarr_scores.py` and `export_sonarr_scores.py`.

**Remember to replace placeholder values like `YOUR_APP_API_KEY_HERE` and example URLs/IPs with your actual settings.**

---

## Radarr (`export_radarr_scores.py`)

### Example 1: Default Localhost HTTP

This is the default configuration often used when Radarr runs on the same machine as the script.

```python
# --- Configuration ---
# ┌─────────────────────────────┐
# │     REQUIRED SETTINGS       │
# └─────────────────────────────┘
RADARR_API_KEY = "YOUR_RADARR_API_KEY_HERE"
RADARR_URL     = "http://127.0.0.1:7878" # Default Radarr port
RADARR_OUTPUT_CSV = "radarr_custom_scores.csv"
# ... other settings ...
```

### Example 2: Using Hostname on Local Network (HTTP)

If Radarr is running on another machine on your network (e.g., a server named `mediaserver`).

```python
# --- Configuration ---
# ┌─────────────────────────────┐
# │     REQUIRED SETTINGS       │
# └─────────────────────────────┘
RADARR_API_KEY = "YOUR_RADARR_API_KEY_HERE"
RADARR_URL     = "http://mediaserver:7878" # Using hostname
RADARR_OUTPUT_CSV = "radarr_custom_scores.csv"
# ... other settings ...
```

### Example 3: Using IP Address on Local Network (HTTP)

Similar to above, but using the IP address of the Radarr server.

```python
# --- Configuration ---
# ┌─────────────────────────────┐
# │     REQUIRED SETTINGS       │
# └─────────────────────────────┘
RADARR_API_KEY = "YOUR_RADARR_API_KEY_HERE"
RADARR_URL     = "http://192.168.1.100:7878" # Using IP address
RADARR_OUTPUT_CSV = "radarr_custom_scores.csv"
# ... other settings ...
```

### Example 4: Using HTTPS with a Domain Name

If Radarr is exposed via a reverse proxy with HTTPS enabled.

```python
# --- Configuration ---
# ┌─────────────────────────────┐
# │     REQUIRED SETTINGS       │
# └─────────────────────────────┘
RADARR_API_KEY = "YOUR_RADARR_API_KEY_HERE"
RADARR_URL     = "https://radarr.yourdomain.com" # Using HTTPS and domain
RADARR_OUTPUT_CSV = "radarr_custom_scores.csv"
# ... other settings ...
```

### Example 5: Using HTTPS with a Subpath

If Radarr is exposed via a reverse proxy under a subpath (e.g., `https://yourserver.com/radarr`).

```python
# --- Configuration ---
# ┌─────────────────────────────┐
# │     REQUIRED SETTINGS       │
# └─────────────────────────────┘
RADARR_API_KEY = "YOUR_RADARR_API_KEY_HERE"
RADARR_URL     = "https://yourserver.com/radarr" # Using HTTPS and subpath
RADARR_OUTPUT_CSV = "radarr_custom_scores.csv"
# ... other settings ...
```
*(Note: Ensure your reverse proxy is configured correctly to pass requests to Radarr)*

---

## Sonarr (`export_sonarr_scores.py`)

The same principles apply to Sonarr.

### Example 1: Default Localhost HTTP

```python
# --- Configuration ---
# ┌─────────────────────────────┐
# │     REQUIRED SETTINGS       │
# └─────────────────────────────┘
SONARR_API_KEY    = "YOUR_SONARR_API_KEY_HERE"
SONARR_URL        = "http://127.0.0.1:8989" # Default Sonarr port
SONARR_OUTPUT_CSV = "sonarr_custom_scores.csv"
# ... other settings ...
```

### Example 2: Using Hostname on Local Network (HTTP)

```python
# --- Configuration ---
# ┌─────────────────────────────┐
# │     REQUIRED SETTINGS       │
# └─────────────────────────────┘
SONARR_API_KEY    = "YOUR_SONARR_API_KEY_HERE"
SONARR_URL        = "http://mediaserver:8989" # Using hostname
SONARR_OUTPUT_CSV = "sonarr_custom_scores.csv"
# ... other settings ...
```

### Example 3: Using IP Address on Local Network (HTTP)

```python
# --- Configuration ---
# ┌─────────────────────────────┐
# │     REQUIRED SETTINGS       │
# └─────────────────────────────┘
SONARR_API_KEY    = "YOUR_SONARR_API_KEY_HERE"
SONARR_URL        = "http://192.168.1.100:8989" # Using IP address
SONARR_OUTPUT_CSV = "sonarr_custom_scores.csv"
# ... other settings ...
```

### Example 4: Using HTTPS with a Domain Name

```python
# --- Configuration ---
# ┌─────────────────────────────┐
# │     REQUIRED SETTINGS       │
# └─────────────────────────────┘
SONARR_API_KEY    = "YOUR_SONARR_API_KEY_HERE"
SONARR_URL        = "https://sonarr.yourdomain.com" # Using HTTPS and domain
SONARR_OUTPUT_CSV = "sonarr_custom_scores.csv"
# ... other settings ...
```

### Example 5: Using HTTPS with a Subpath

```python
# --- Configuration ---
# ┌─────────────────────────────┐
# │     REQUIRED SETTINGS       │
# └─────────────────────────────┘
SONARR_API_KEY    = "YOUR_SONARR_API_KEY_HERE"
SONARR_URL        = "https://yourserver.com/sonarr" # Using HTTPS and subpath
SONARR_OUTPUT_CSV = "sonarr_custom_scores.csv"
# ... other settings ...
```

---

Remember to adjust `MAX_WORKERS`, `API_TIMEOUT`, and `REQUEST_DELAY` based on your specific environment and needs, as described in the main `README.md` and `USAGE-GUIDE.md`.
