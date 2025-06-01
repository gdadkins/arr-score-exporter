# API Reference

## Command Line Interface

### Basic CSV Export (`arr-export`)

**Main Command:**
```bash
arr-export [OPTIONS] COMMAND [ARGS]...
```

**Global Options:**
- `--config, -c PATH`: Path to configuration file
- `--verbose, -v`: Enable verbose output
- `--output-dir, -o PATH`: Output directory for exports
- `--help`: Show help message

**Commands:**

#### `arr-export radarr`
Export Radarr scores to CSV format.
```bash
arr-export radarr
arr-export --verbose radarr
arr-export --config custom.yaml radarr
```

#### `arr-export sonarr`
Export Sonarr scores to CSV format.
```bash
arr-export sonarr
```

#### `arr-export both`
Export both Radarr and Sonarr to CSV.
```bash
arr-export both
```

#### `arr-export test-config`
Test configuration and API connectivity.
```bash
arr-export test-config
```

### Enhanced Dashboard Export (`arr-export-enhanced`)

**Main Command:**
```bash
arr-export-enhanced [OPTIONS] COMMAND [ARGS]...
```

**Commands:**

#### `arr-export-enhanced SERVICE`
Collect fresh data and generate reports (recommended for up-to-date results).
```bash
arr-export-enhanced radarr    # Fresh data collection + CSV + HTML dashboard
arr-export-enhanced sonarr    # Fresh data collection + CSV + HTML dashboard
```

#### `arr-export-enhanced report --service SERVICE`
Generate HTML dashboard from cached data (no API calls).
```bash
arr-export-enhanced report --service radarr
arr-export-enhanced report --service sonarr  
arr-export-enhanced report --service both
```

#### `arr-export-enhanced validate-config`
Validate configuration and test API connectivity.
```bash
arr-export-enhanced validate-config
```

### Output Comparison

| Feature | `arr-export` | `arr-export-enhanced` |
|---------|--------------|----------------------|
| CSV Export | ✅ | ✅ |
| HTML Dashboard | ❌ | ✅ |
| Upgrade Analysis | ❌ | ✅ |
| Historical Tracking | ❌ | ✅ |
| Interactive Charts | ❌ | ✅ |
| Health Scoring | ❌ | ✅ |
| File Size Display | GB | TB (for large libraries) |
| Export Functions | Basic | CSV/Excel/PDF |
| API Data Collection | Real-time | Real-time + Cached |

## Python API

### Configuration
```python
from arr_score_exporter.config import Config

config = Config()  # Load from default locations
config = Config('/path/to/config.yaml')  # Load specific file

# Check service availability
if config.is_radarr_enabled():
    print(f"Radarr enabled at {config.radarr_url}")
```

### Basic CSV Export
```python
from arr_score_exporter.exporters.radarr import RadarrExporter
from arr_score_exporter.config import Config

config = Config()
exporter = RadarrExporter(config)

# Export to CSV
csv_path = exporter.export_to_csv()
print(f"CSV exported to: {csv_path}")
```

### Enhanced Dashboard Export
```python
from arr_score_exporter.exporters.enhanced_radarr import EnhancedRadarrExporter
from arr_score_exporter.config import Config
from arr_score_exporter.models import DatabaseManager

config = Config()
db = DatabaseManager()
exporter = EnhancedRadarrExporter(config, db)

# Full export with analysis
results = exporter.export_with_analysis()
print(f"Dashboard: {results['dashboard_path']}")
print(f"Upgrade candidates: {results['upgrade_candidates']}")
```

### Database Operations
```python
from arr_score_exporter.models import DatabaseManager

db = DatabaseManager()

# Get library statistics
stats = db.calculate_library_stats("radarr")
print(f"Total files: {stats.total_files}")
print(f"Average score: {stats.avg_score:.1f}")

# Get upgrade candidates
candidates = db.get_upgrade_candidates(-50, "radarr")
for candidate in candidates[:5]:
    print(f"{candidate.title}: Priority {candidate.priority}")
```

## Configuration Schema

### Required Fields
```yaml
radarr:
  url: "http://192.168.1.100:7878"
  api_key: "your_radarr_api_key"
  enabled: true

sonarr:
  url: "http://192.168.1.100:8989"  
  api_key: "your_sonarr_api_key"
  enabled: true
```

### Optional Settings
```yaml
export:
  output_dir: "exports"              # Output directory
  max_workers: 5                     # Parallel processing
  retry_attempts: 3                  # API retry count
  timeout: 30                        # Request timeout
  
dashboard:
  show_upgrade_candidates: 20        # Dashboard limits
  show_format_analysis: 15           # Format analysis entries
  theme: "light"                     # light/dark theme
  
logging:
  level: "INFO"                      # Log level
  console_output: true               # Console logging
```

### Environment Variables
Any configuration value can be overridden:
```bash
export RADARR_URL="http://localhost:7878"
export RADARR_API_KEY="your_key"
export ARR_MAX_WORKERS="3"
export ARR_OUTPUT_DIR="/data/exports"
```

## Return Value Schemas

### Basic Export Results
```python
{
    "processed": 3231,                # Files processed
    "csv_path": "exports/radarr_export_20241129.csv",
    "duration_seconds": 25.3,         # Processing time
    "errors": 0                       # Error count
}
```

### Enhanced Export Results  
```python
{
    "processed": 3231,                # Files processed
    "stored": 3015,                   # Files stored in database
    "upgrade_candidates": 1252,       # Upgrade candidates found
    "csv_path": "exports/radarr_export_20241129.csv",
    "dashboard_path": "exports/radarr_dashboard_20241129.html",
    "duration_seconds": 45.2,
    "analysis_results": {
        "library_health_score": 78.5,
        "health_grade": "B",
        "total_files": 3231,
        "total_size_display": "21.6 TB"  // Automatically displayed in TB for large libraries
    }
}
```

### Media File Data Structure
```python
{
    "file_id": 123,
    "title": "The Matrix",
    "relative_path": "Movies/The Matrix (1999)/Matrix.2160p.mkv",
    "total_score": 6150,
    "quality_profile_name": "4K Remux",
    "quality": "Remux-2160p",
    "codec": "x265",
    "resolution": "2160p",
    "size_bytes": 45678901234,
    "custom_formats": [
        {
            "name": "Remux Tier 01",
            "score": 6000
        },
        {
            "name": "HDR10+", 
            "score": 150
        }
    ],
    "service_type": "radarr",
    "recorded_at": "2024-11-29T14:30:22Z"
}
```

## Error Handling

### Exit Codes
- `0`: Success
- `1`: Configuration error
- `2`: API connection error
- `3`: Database error
- `4`: Export processing error
- `5`: Analysis generation error

### Common Exceptions
```python
# Configuration errors
from arr_score_exporter.config import Config
try:
    config = Config()
except FileNotFoundError:
    print("Config file not found")
except ValueError as e:
    print(f"Invalid configuration: {e}")

# API connection errors  
from arr_score_exporter.api_client import ArrApiClient
try:
    client = ArrApiClient(url, api_key)
    status = client.test_connection()
except ConnectionError:
    print("Cannot connect to service")
except HTTPError as e:
    print(f"API error: {e}")
```

## Performance Tuning

### Configuration by Library Size

**Small (<1000 files):**
```yaml
export:
  max_workers: 5
  timeout: 30
```

**Medium (1000-5000 files):**
```yaml
export:
  max_workers: 5
  timeout: 45
```

**Large (5000+ files):**
```yaml
export:
  max_workers: 3
  retry_attempts: 5
  timeout: 60
```

### Memory Requirements
- **Basic CSV**: 100-200MB for typical libraries
- **Enhanced Dashboard**: 200-400MB for analysis processing
- **Large Libraries**: 4GB+ RAM recommended for 5000+ files

## Legacy Scripts

Original monolithic scripts remain available:
```bash
python legacy/export_radarr_scores.py
python legacy/export_sonarr_scores.py
```

These provide simple CSV export without database or dashboard features.