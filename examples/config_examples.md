# Configuration Examples

This file shows various YAML configuration examples for the modern `arr-export` and `arr-export-enhanced` CLI tools.

**⚠️ Note**: For legacy Python scripts (`export_radarr_scores.py` and `export_sonarr_scores.py`) configuration, see the `legacy/` folder. The examples below are for the modern CLI tools.

**Remember to replace placeholder values like `YOUR_API_KEY_HERE` with your actual API keys.**

---

## Basic Configuration (`config.yaml`)

### Example 1: Local Setup (Default Ports)

```yaml
radarr:
  url: "http://127.0.0.1:7878"
  api_key: "YOUR_RADARR_API_KEY_HERE"
  enabled: true

sonarr:
  url: "http://127.0.0.1:8989"
  api_key: "YOUR_SONARR_API_KEY_HERE"
  enabled: true

export:
  output_dir: "exports"
  max_workers: 5
```

### Example 2: Network Server Setup

```yaml
radarr:
  url: "http://192.168.1.100:7878"
  api_key: "YOUR_RADARR_API_KEY_HERE"
  enabled: true

sonarr:
  url: "http://192.168.1.100:8989"
  api_key: "YOUR_SONARR_API_KEY_HERE"  
  enabled: true

export:
  output_dir: "/data/exports"
  max_workers: 5
  retry_attempts: 3
  timeout: 30
```

### Example 3: HTTPS with Domain Names

```yaml
radarr:
  url: "https://radarr.yourdomain.com"
  api_key: "YOUR_RADARR_API_KEY_HERE"
  enabled: true

sonarr:
  url: "https://sonarr.yourdomain.com"
  api_key: "YOUR_SONARR_API_KEY_HERE"
  enabled: true

export:
  output_dir: "exports"
  max_workers: 3  # Reduced for external connections
  timeout: 60     # Longer timeout for internet connections
```

### Example 4: Reverse Proxy with Subpaths

```yaml
radarr:
  url: "https://yourserver.com/radarr"
  api_key: "YOUR_RADARR_API_KEY_HERE"
  enabled: true

sonarr:
  url: "https://yourserver.com/sonarr"
  api_key: "YOUR_SONARR_API_KEY_HERE"
  enabled: true

export:
  output_dir: "exports"
  max_workers: 4
  timeout: 45
```

---

## Performance Tuning Examples

### Large Library Configuration (5000+ files)

```yaml
radarr:
  url: "http://192.168.1.100:7878"
  api_key: "YOUR_RADARR_API_KEY_HERE"
  enabled: true

sonarr:
  url: "http://192.168.1.100:8989"
  api_key: "YOUR_SONARR_API_KEY_HERE"
  enabled: true

export:
  output_dir: "exports"
  max_workers: 3          # Reduced for stability
  retry_attempts: 5       # More retries
  timeout: 60             # Longer timeout
  
dashboard:
  show_upgrade_candidates: 50   # Show more candidates
  show_format_analysis: 20      # Extended format analysis
```

### Slow Network Configuration

```yaml
radarr:
  url: "https://remote-radarr.example.com"
  api_key: "YOUR_RADARR_API_KEY_HERE"
  enabled: true

sonarr:
  url: "https://remote-sonarr.example.com"
  api_key: "YOUR_SONARR_API_KEY_HERE"
  enabled: true

export:
  output_dir: "exports"
  max_workers: 2          # Very conservative
  retry_attempts: 7       # Many retries
  retry_delay: 3          # Longer delays
  timeout: 120            # Very long timeout
```

### Development/Testing Configuration

```yaml
radarr:
  url: "http://localhost:7878"
  api_key: "test_api_key_here"
  enabled: true

sonarr:
  url: "http://localhost:8989"
  api_key: "test_api_key_here"
  enabled: false  # Disable for testing

export:
  output_dir: "test_output"
  max_workers: 2
  
logging:
  level: "DEBUG"
  console_output: true
```

---

## Environment Variable Override Examples

You can override any configuration value using environment variables:

### Basic Environment Setup

```bash
# API Configuration
export RADARR_URL="http://192.168.1.100:7878"
export RADARR_API_KEY="your_radarr_api_key"
export SONARR_URL="http://192.168.1.100:8989"
export SONARR_API_KEY="your_sonarr_api_key"

# Performance Settings
export ARR_MAX_WORKERS="3"
export ARR_OUTPUT_DIR="/data/exports"
export ARR_TIMEOUT="60"

# Run with environment config
arr-export radarr
```

### Docker Environment File (`.env`)

```bash
# .env file for Docker usage
RADARR_URL=http://radarr:7878
RADARR_API_KEY=your_radarr_api_key_here
SONARR_URL=http://sonarr:8989
SONARR_API_KEY=your_sonarr_api_key_here
ARR_MAX_WORKERS=3
ARR_OUTPUT_DIR=/exports
```

---

## Specialized Configurations

### Single Service Configuration (Radarr Only)

```yaml
radarr:
  url: "http://192.168.1.100:7878"
  api_key: "YOUR_RADARR_API_KEY_HERE"
  enabled: true

sonarr:
  enabled: false  # Completely disable Sonarr

export:
  output_dir: "radarr_only_exports"
  max_workers: 5
```

### Custom Output and Dashboard Settings

```yaml
radarr:
  url: "http://192.168.1.100:7878"
  api_key: "YOUR_RADARR_API_KEY_HERE"
  enabled: true

sonarr:
  url: "http://192.168.1.100:8989"
  api_key: "YOUR_SONARR_API_KEY_HERE"
  enabled: true

export:
  output_dir: "custom_exports"
  max_workers: 5

dashboard:
  show_upgrade_candidates: 100    # Show more candidates
  show_format_analysis: 25        # Extended analysis
  theme: "dark"                   # Dark theme (if supported)

logging:
  level: "INFO"
  console_output: true
```

---

## Getting API Keys

To get your API keys:

1. **Radarr**: Settings → General → Security → API Key
2. **Sonarr**: Settings → General → Security → API Key

## Testing Configuration

```bash
# Test your configuration
arr-export test-config

# Test with specific config file
arr-export --config /path/to/config.yaml test-config

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

## Usage with Examples

```bash
# Use configuration examples
cp examples/config_examples.md config.yaml
# Edit config.yaml with your actual values

# Run export
arr-export-enhanced radarr
arr-export-enhanced report --service radarr
```

---

For more configuration options, see:
- [USAGE-GUIDE.md](../USAGE-GUIDE.md) - Detailed usage examples
- [docs/API_REFERENCE.md](../docs/API_REFERENCE.md) - Complete configuration schema
- [config.yaml.example](../config.yaml.example) - Template configuration file