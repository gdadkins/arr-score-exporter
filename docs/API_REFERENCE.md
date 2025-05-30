# Enhanced API Reference

## Enhanced Command Line Interface

### Main Command
```bash
arr-export [OPTIONS] COMMAND [ARGS]...
```

**Global Options:**
- `--config, -c PATH`: Path to configuration file
- `--verbose, -v`: Enable verbose output with rich formatting
- `--output-dir, -o PATH`: Output directory for exports
- `--help`: Show help message

### Available Commands

#### `radarr`
Export scores from Radarr with intelligent analysis.

```bash
arr-export radarr
```

**Features:**
- Extracts all movie files and custom format scores
- Generates interactive HTML dashboard
- Creates detailed CSV export
- Identifies upgrade candidates
- Analyzes custom format effectiveness

**Output:**
- `radarr_export_YYYYMMDD_HHMMSS.csv`: Detailed movie data
- `radarr_dashboard_YYYYMMDD_HHMMSS.html`: Interactive dashboard
- Database updates with historical tracking

#### `sonarr`
Export scores from Sonarr with intelligent analysis.

```bash
arr-export sonarr
```

**Features:**
- Extracts all series/episode files and scores
- Generates interactive HTML dashboard
- Creates detailed CSV export
- Identifies upgrade candidates
- Analyzes custom format effectiveness

#### `both`
Export scores from both Radarr and Sonarr.

```bash
arr-export both
```

**Process:**
1. Runs Radarr export first
2. Runs Sonarr export second
3. Generates combined summary statistics
4. Creates separate dashboards for each service

#### `test-config`
Validate configuration and test API connectivity.

```bash
arr-export test-config
```

**Output Example:**
```
🔧 Testing Configuration...

📋 Configuration Status:
  ✅ Config file loaded: config.yaml
  ✅ Radarr: http://192.168.3.229:7878
  ✅ Sonarr: http://192.168.3.229:8989

🌐 API Connectivity:
  ✅ Radarr API: Connected (3,231 movies)
  ✅ Sonarr API: Connected (45 series)

📊 Database Status:
  ✅ Database: ~/.arr-score-exporter/library.db
  ✅ Tables: All initialized
  📈 Records: 3,231 media files

✅ All systems ready!
```

### Windows Launcher
For Windows users, a convenient launcher script is available:

```bash
# Windows-specific launcher with enhanced output
python run_enhanced.py radarr
python run_enhanced.py sonarr
python run_enhanced.py both
python run_enhanced.py test-config
```

## Enhanced Python API

### Core Classes

#### Enhanced Config
Advanced configuration management with validation and environment support.

```python
from arr_score_exporter.config import Config

# Load from default locations with automatic discovery
config = Config()

# Load from specific file
config = Config('/path/to/config.yaml')

# Access configuration values
radarr_url = config.radarr_url
max_workers = config.max_workers
output_dir = config.output_dir

# Check service availability
if config.is_radarr_enabled():
    print(f"Radarr enabled at {config.radarr_url}")
```

**Enhanced Properties:**
- `radarr_url: str` - Radarr base URL
- `radarr_api_key: str` - Radarr API key
- `sonarr_url: str` - Sonarr base URL
- `sonarr_api_key: str` - Sonarr API key
- `max_workers: int` - Parallel processing threads
- `output_dir: str` - Export output directory
- `retry_attempts: int` - API retry count
- `retry_delay: float` - Delay between retries

**Enhanced Methods:**
- `is_radarr_enabled() -> bool` - Check if Radarr is configured
- `is_sonarr_enabled() -> bool` - Check if Sonarr is configured
- `validate() -> bool` - Validate all configuration
- `get_export_settings() -> Dict` - Get export configuration
- `get_database_path() -> Path` - Get database file path

#### Enhanced RadarrExporter
Advanced Radarr integration with database persistence and analysis.

```python
from arr_score_exporter.exporters.radarr import RadarrExporter
from arr_score_exporter.config import Config
from arr_score_exporter.models import DatabaseManager

config = Config()
db = DatabaseManager()
exporter = RadarrExporter(config, db)

# Full export with analysis
results = exporter.export_with_analysis()
print(f"Movies processed: {results['processed']}")
print(f"Files stored: {results['stored']}")
print(f"Upgrade candidates: {results['upgrade_candidates']}")
print(f"Dashboard: {results['dashboard_path']}")

# Test connection with detailed info
connection_info = exporter.test_connection_detailed()
print(f"Movies: {connection_info['movie_count']}")
print(f"Quality profiles: {connection_info['profile_count']}")
```

**Enhanced Methods:**
- `export_with_analysis() -> Dict[str, Any]` - Full export with dashboard
- `export_to_database() -> Dict[str, int]` - Store data in database
- `generate_dashboard() -> str` - Create HTML dashboard
- `get_upgrade_candidates() -> List[MediaFile]` - Get upgrade suggestions
- `test_connection_detailed() -> Dict[str, Any]` - Detailed connection test

#### Enhanced SonarrExporter
Advanced Sonarr integration with episode-level analysis.

```python
from arr_score_exporter.exporters.sonarr import SonarrExporter
from arr_score_exporter.config import Config
from arr_score_exporter.models import DatabaseManager

config = Config()
db = DatabaseManager()
exporter = SonarrExporter(config, db)

# Full export with analysis
results = exporter.export_with_analysis()
print(f"Series processed: {results['series_processed']}")
print(f"Episodes processed: {results['episodes_processed']}")
print(f"Files stored: {results['stored']}")

# Get series-specific insights
series_analysis = exporter.analyze_by_series()
for series in series_analysis[:5]:
    print(f"{series['title']}: {series['avg_score']:.1f} avg score")
```

**Enhanced Methods:**
- `export_with_analysis() -> Dict[str, Any]` - Full export with dashboard
- `analyze_by_series() -> List[Dict]` - Series-level analysis
- `get_episode_upgrade_candidates() -> List[MediaFile]` - Episode suggestions
- `get_series_statistics() -> Dict[str, Any]` - Series statistics

#### Enhanced CSV and Dashboard Writers
Advanced export utilities with rich formatting and dashboard generation.

```python
from arr_score_exporter.utils.csv_writer import CSVWriter
from arr_score_exporter.reporting.dashboard import DashboardGenerator

# Enhanced CSV writer
writer = CSVWriter(output_dir="exports")

# Write comprehensive movie data
media_files = [...]  # List of MediaFile objects
csv_path = writer.write_enhanced_csv(media_files, "movies", "radarr")
print(f"CSV exported to: {csv_path}")

# Generate interactive dashboard
dashboard = DashboardGenerator()
html_path = dashboard.generate_dashboard(
    service_type="radarr",
    media_files=media_files,
    stats=library_stats,
    analysis_results=analysis
)
print(f"Dashboard: {html_path}")
```

**Enhanced Methods:**
- `write_enhanced_csv(files: List[MediaFile], prefix: str, service: str) -> str`
- `write_upgrade_candidates_csv(candidates: List[UpgradeCandidate]) -> str`
- `write_format_effectiveness_csv(analysis: List[CustomFormatEffectiveness]) -> str`

#### Database Models
Comprehensive data models for persistence and analysis.

```python
from arr_score_exporter.models import DatabaseManager, MediaFile, LibraryStats
from arr_score_exporter.analysis import IntelligentAnalyzer

# Database operations
db = DatabaseManager()

# Store media file with full metadata
media_file = MediaFile(
    file_id=123,
    title="The Matrix",
    total_score=150,
    custom_formats=[...],
    # ... additional fields
)
success = db.store_media_file(media_file)

# Get library statistics
stats = db.calculate_library_stats("radarr")
print(f"Total files: {stats.total_files}")
print(f"Average score: {stats.avg_score:.1f}")

# Intelligent analysis
analyzer = IntelligentAnalyzer(db)
candidates = analyzer.identify_upgrade_candidates("radarr")
format_analysis = analyzer.analyze_custom_format_effectiveness("radarr")
```

**Database Features:**
- Thread-safe SQLite operations with WAL mode
- Historical score tracking and trend analysis
- Comprehensive media file metadata storage
- Export run logging and audit trail

### Advanced Usage

#### Custom Analysis Workflows
```python
from arr_score_exporter.analysis import IntelligentAnalyzer
from arr_score_exporter.models import DatabaseManager
from arr_score_exporter.config import Config

# Setup
config = Config()
db = DatabaseManager()
analyzer = IntelligentAnalyzer(db)

# Generate comprehensive health report
health_report = analyzer.generate_library_health_report("radarr")
print(f"Health Grade: {health_report.health_grade}")
print(f"Health Score: {health_report.health_score:.1f}")

# Analyze specific aspects
upgrade_candidates = analyzer.identify_upgrade_candidates("radarr", min_score_threshold=-100)
critical_candidates = [c for c in upgrade_candidates if c.priority == 1]

format_effectiveness = analyzer.analyze_custom_format_effectiveness("radarr")
top_formats = [f for f in format_effectiveness if f.impact_rating == "high"]

quality_analysis = analyzer.analyze_quality_profiles("radarr")
best_profiles = [p for p in quality_analysis if p.effectiveness_rating == "excellent"]
```

#### Database Query Examples
```python
from arr_score_exporter.models import DatabaseManager

db = DatabaseManager()

# Custom queries for specific insights
with db._get_connection() as conn:
    # Find highest scoring movies
    top_movies = conn.execute("""
        SELECT title, total_score, quality_profile_name
        FROM media_files 
        WHERE service_type = 'radarr' AND total_score > 100
        ORDER BY total_score DESC
        LIMIT 10
    """).fetchall()
    
    # Get score trends for last 30 days
    trends = conn.execute("""
        SELECT DATE(timestamp) as date, 
               COUNT(*) as changes,
               AVG(total_score) as avg_score
        FROM score_history 
        WHERE timestamp >= datetime('now', '-30 days')
        GROUP BY DATE(timestamp)
        ORDER BY date
    """).fetchall()
```

#### Custom Dashboard Components
```python
from arr_score_exporter.reporting.dashboard import DashboardGenerator
from arr_score_exporter.models import DatabaseManager

# Create custom dashboard with specific data
db = DatabaseManager()
generator = DashboardGenerator()

# Get data for dashboard
stats = db.calculate_library_stats("radarr")
upgrade_candidates = db.get_upgrade_candidates(-50, "radarr")
trends = db.get_score_trends(30, "radarr")

# Generate with custom title and styling
dashboard_path = generator.generate_dashboard(
    service_type="radarr",
    title="My Movie Library Analysis",
    stats=stats,
    upgrade_candidates=upgrade_candidates[:20],
    trends=trends,
    custom_css="/* custom styles */"
)
```

#### Comprehensive Error Handling and Logging
```python
from arr_score_exporter.exporters.radarr import RadarrExporter
from arr_score_exporter.config import Config
from arr_score_exporter.models import DatabaseManager
import logging
from pathlib import Path

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arr-exporter.log'),
        logging.StreamHandler()
    ]
)

try:
    # Initialize with error handling
    config = Config()
    if not config.validate():
        raise ValueError("Invalid configuration")
        
    db = DatabaseManager()
    exporter = RadarrExporter(config, db)
    
    # Test connectivity with detailed results
    connection_test = exporter.test_connection_detailed()
    if not connection_test['success']:
        raise ConnectionError(f"Radarr connection failed: {connection_test['error']}")
        
    logging.info(f"Connected to Radarr: {connection_test['movie_count']} movies")
    
    # Run export with comprehensive error tracking
    results = exporter.export_with_analysis()
    
    # Report results
    if results['errors'] > 0:
        logging.warning(f"Export completed with {results['errors']} errors")
        logging.info(f"Successfully processed: {results['processed']} movies")
    else:
        logging.info(f"Export completed successfully: {results['processed']} movies")
        
    # Check dashboard generation
    if results.get('dashboard_path'):
        dashboard_path = Path(results['dashboard_path'])
        if dashboard_path.exists():
            logging.info(f"Dashboard generated: {dashboard_path}")
        else:
            logging.warning("Dashboard generation failed")
            
except Exception as e:
    logging.error(f"Export failed: {e}", exc_info=True)
    raise
```

## Enhanced Configuration Schema

### Complete Configuration Example
```yaml
# Radarr Configuration
radarr:
  url: "http://192.168.3.229:7878"
  api_key: "your_radarr_api_key_here"
  enabled: true

# Sonarr Configuration
sonarr:
  url: "http://192.168.3.229:8989"
  api_key: "your_sonarr_api_key_here"
  enabled: true

# Export Settings
export:
  # Output configuration
  output_dir: "exports"              # Output directory for files
  generate_dashboard: true           # Generate HTML dashboards
  
  # Performance settings
  max_workers: 5                     # Parallel processing threads
  retry_attempts: 3                  # API retry count
  retry_delay: 1                     # Delay between retries (seconds)
  timeout: 30                        # Request timeout (seconds)
  
  # Database settings
  database_path: "~/.arr-score-exporter/library.db"
  
  # Analysis settings
  upgrade_candidate_threshold: -50   # Minimum score for upgrade candidates
  enable_trend_analysis: true        # Track score changes over time
  
# Dashboard Configuration (optional)
dashboard:
  title: "My Media Library Analysis"  # Custom dashboard title
  theme: "dark"                      # light/dark theme
  show_upgrade_candidates: 20        # Number of candidates to show
  show_format_analysis: 15           # Number of formats to analyze
  
# Logging Configuration (optional)
logging:
  level: "INFO"                      # DEBUG, INFO, WARNING, ERROR
  file: "arr-exporter.log"           # Log file path
  console_output: true               # Enable console logging
  rich_formatting: true              # Enable rich terminal formatting
```

### Required Fields
- `radarr.url` and `radarr.api_key` (if Radarr export desired)
- `sonarr.url` and `sonarr.api_key` (if Sonarr export desired)
- At least one service must be enabled

### Default Values
```yaml
# Export defaults
export:
  output_dir: "exports"
  max_workers: 5
  retry_attempts: 3
  retry_delay: 1
  timeout: 30
  generate_dashboard: true
  upgrade_candidate_threshold: -50
  enable_trend_analysis: true

# Dashboard defaults
dashboard:
  theme: "light"
  show_upgrade_candidates: 20
  show_format_analysis: 15

# Logging defaults
logging:
  level: "INFO"
  console_output: true
  rich_formatting: true
```

### Environment Variable Overrides
Any configuration value can be overridden with environment variables:

```bash
# Service configuration
export RADARR_URL="http://localhost:7878"
export RADARR_API_KEY="your_key_here"
export SONARR_URL="http://localhost:8989"
export SONARR_API_KEY="your_key_here"

# Export settings
export ARR_MAX_WORKERS="3"
export ARR_OUTPUT_DIR="/path/to/exports"
export ARR_RETRY_ATTEMPTS="5"

# Logging
export ARR_LOG_LEVEL="DEBUG"
export ARR_LOG_FILE="debug.log"
```

## Enhanced Return Value Schemas

### Export Results (Enhanced)
```python
{
    "processed": 3231,                    # Total movies/episodes processed
    "stored": 3015,                      # Files successfully stored in database
    "errors": 0,                         # Items that failed processing
    "upgrade_candidates": 1252,          # Files identified for potential upgrade
    "csv_path": "exports/radarr_export_20241129_143022.csv",
    "dashboard_path": "exports/radarr_dashboard_20241129_143022.html",
    "duration_seconds": 45.2,            # Export duration
    "api_calls_made": 3231,              # Total API calls
    "database_updates": {
        "new_files": 0,
        "updated_files": 3015,
        "score_changes": 156
    },
    "analysis_results": {
        "library_health_score": 78.5,
        "health_grade": "B",
        "custom_formats_analyzed": 95,
        "quality_profiles_analyzed": 16
    }
}
```

### Enhanced Media File Data Structure
```python
# Enhanced MediaFile object
{
    "file_id": 123,
    "title": "The Matrix",
    "relative_path": "Movies/The Matrix (1999)/The Matrix.2160p.UHD.BluRay.x265.mkv",
    "total_score": 6150,
    "quality_profile_id": 1,
    "quality_profile_name": "4K Remux",
    "quality": "Remux-2160p",
    "codec": "x265",
    "resolution": "2160p",
    "size_bytes": 45678901234,
    "custom_formats": [
        {
            "name": "Remux Tier 01",
            "score": 6000,
            "format_id": 1,
            "category": "Quality"
        },
        {
            "name": "HDR10+",
            "score": 150,
            "format_id": 15,
            "category": "HDR"
        }
    ],
    "service_type": "radarr",
    "movie_id": 456,
    "imdb_id": "tt0133093",
    "tmdb_id": 603,
    "recorded_at": "2024-11-29T14:30:22Z",
    "unique_identifier": "radarr:456:123"
}

# Analysis Results
{
    "upgrade_candidates": [
        {
            "media_file": MediaFile,
            "reason": "Score 89 points below library average; Has 2 negative-scoring format(s)",
            "priority": 1,  # 1=critical, 2=high, 3=medium, 4=low
            "potential_score_gain": 62,
            "recommendation": "Replace release to avoid 'Cam' format (score: -10000)"
        }
    ],
    "custom_format_effectiveness": [
        {
            "format_name": "Remux Tier 01",
            "usage_count": 523,
            "avg_score_contribution": 6981.2,
            "files_with_format": 523,
            "impact_rating": "high",
            "recommendations": []
        }
    ],
    "library_health": {
        "health_score": 78.5,
        "health_grade": "B",
        "total_files": 3231,
        "recommendations": ["Focus on upgrading files with negative scores first"],
        "achievements": ["Most files have positive quality scores"],
        "warnings": ["1252 files need immediate attention"]
    }
}
```

## Error Handling and Troubleshooting

### Configuration Errors
- `FileNotFoundError: No configuration file found` - Copy config.yaml.example to config.yaml
- `RuntimeError: Failed to load configuration` - Check YAML syntax and indentation
- `ValueError: Invalid configuration values` - Verify URLs and API keys

### Database Errors
- `sqlite3.OperationalError: database is locked` - **FIXED**: Enhanced connection management with WAL mode and retry logic
- `PermissionError: Cannot write to database` - Check write permissions to database directory
- `sqlite3.DatabaseError: no such table` - Database schema initialization failed

### API Connection Errors
- `ConnectionError: Cannot connect to Radarr/Sonarr` - Verify service is running and URL is correct
- `HTTPError 401: Unauthorized` - Check API key validity
- `HTTPError 404: Not Found` - Verify API endpoint and service version
- `HTTPError 429: Too Many Requests` - Automatic retry with exponential backoff
- `HTTPError 502/503: Service Unavailable` - Service temporarily down, retry later

### Processing Errors
- `ImportError: Missing required dependencies` - Run `pip install -e .[dev]`
- `TimeoutError: Request timeout` - Increase timeout in configuration
- `MemoryError: Insufficient memory` - Reduce max_workers or increase system RAM
- `JSON decode error` - Malformed API response, check service health

### Analysis Errors
- `No data found for analysis` - Ensure files have been exported to database
- `Empty custom format data` - **FIXED**: Improved correlation analysis logic
- `Score trends empty` - Expected on first run, requires historical data

### Recovery Procedures
```python
# Test and recover from common issues
from arr_score_exporter.config import Config
from arr_score_exporter.models import DatabaseManager

# 1. Test configuration
try:
    config = Config()
    if config.validate():
        print("✅ Configuration valid")
except Exception as e:
    print(f"❌ Configuration error: {e}")

# 2. Test database
try:
    db = DatabaseManager()
    with db._get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) FROM media_files").fetchone()
        print(f"✅ Database accessible: {result[0]} files")
except Exception as e:
    print(f"❌ Database error: {e}")

# 3. Test API connectivity
from arr_score_exporter.api_client import ArrApiClient
try:
    client = ArrApiClient(config.radarr_url, config.radarr_api_key)
    status = client.test_connection()
    print(f"✅ API connected: {status}")
except Exception as e:
    print(f"❌ API error: {e}")
```

## Production Deployment

### Environment Variables
Complete environment variable support for containerized deployments:

```bash
# Core service configuration
export RADARR_URL="http://radarr:7878"
export RADARR_API_KEY="abc123..."
export SONARR_URL="http://sonarr:8989"
export SONARR_API_KEY="def456..."

# Performance tuning
export ARR_MAX_WORKERS="3"              # Reduce for limited resources
export ARR_RETRY_ATTEMPTS="5"            # Increase for unreliable networks
export ARR_TIMEOUT="60"                  # Increase for slow systems

# Output configuration
export ARR_OUTPUT_DIR="/data/exports"    # Persistent volume mount
export ARR_DATABASE_PATH="/data/library.db"

# Dashboard customization
export ARR_DASHBOARD_TITLE="Production Library"
export ARR_DASHBOARD_THEME="dark"

# Logging
export ARR_LOG_LEVEL="INFO"              # Reduce verbosity in production
export ARR_LOG_FILE="/logs/arr-export.log"
export ARR_RICH_FORMATTING="false"       # Disable for non-interactive environments
```

### Docker Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  arr-score-exporter:
    build: .
    environment:
      - RADARR_URL=http://radarr:7878
      - RADARR_API_KEY=${RADARR_API_KEY}
      - SONARR_URL=http://sonarr:8989
      - SONARR_API_KEY=${SONARR_API_KEY}
      - ARR_OUTPUT_DIR=/data/exports
      - ARR_DATABASE_PATH=/data/library.db
    volumes:
      - ./exports:/data/exports
      - ./database:/data
    depends_on:
      - radarr
      - sonarr
    command: ["arr-export", "both"]
```

### Scheduled Execution
```bash
# Cron job for regular exports
# Run daily at 2 AM
0 2 * * * /usr/local/bin/arr-export both >> /var/log/arr-export.log 2>&1

# Systemd timer for more advanced scheduling
# /etc/systemd/system/arr-export.timer
[Unit]
Description=Run Arr Score Exporter
Requires=arr-export.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

## Advanced Integration Examples

### GitHub Actions with Dashboard Publishing
```yaml
name: Library Analysis and Dashboard
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:    # Manual trigger

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install arr-score-exporter
        run: |
          pip install -e .
          pip install -e .[dev]
      
      - name: Run analysis and generate dashboard
        env:
          RADARR_API_KEY: ${{ secrets.RADARR_API_KEY }}
          SONARR_API_KEY: ${{ secrets.SONARR_API_KEY }}
          ARR_OUTPUT_DIR: ./public
        run: |
          arr-export both --verbose
          
      - name: Upload dashboard artifacts
        uses: actions/upload-artifact@v3
        with:
          name: library-dashboard
          path: ./public/*.html
          
      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

### Advanced Docker Setup with Health Monitoring
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .
RUN pip install -e .

# Create non-root user
RUN useradd -m -s /bin/bash arrexporter
USER arrexporter

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD arr-export test-config || exit 1

# Default command
CMD ["arr-export", "both", "--verbose"]
```

### Kubernetes CronJob
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: arr-score-exporter
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: arr-exporter
            image: arr-score-exporter:latest
            env:
            - name: RADARR_URL
              value: "http://radarr.media.svc.cluster.local:7878"
            - name: RADARR_API_KEY
              valueFrom:
                secretKeyRef:
                  name: arr-secrets
                  key: radarr-api-key
            - name: ARR_OUTPUT_DIR
              value: "/data/exports"
            volumeMounts:
            - name: exports
              mountPath: /data/exports
            - name: database
              mountPath: /data/database
          volumes:
          - name: exports
            persistentVolumeClaim:
              claimName: arr-exports-pvc
          - name: database
            persistentVolumeClaim:
              claimName: arr-database-pvc
          restartPolicy: OnFailure
```

### Monitoring and Alerting Integration
```python
# Custom monitoring script
from arr_score_exporter.models import DatabaseManager
from datetime import datetime, timedelta
import requests

def check_export_health():
    """Monitor export health and send alerts."""
    db = DatabaseManager()
    
    # Check last successful export
    with db._get_connection() as conn:
        last_export = conn.execute("""
            SELECT timestamp, success FROM export_runs 
            WHERE success = 1 
            ORDER BY timestamp DESC 
            LIMIT 1
        """).fetchone()
        
    if not last_export:
        send_alert("No successful exports found")
        return
        
    last_time = datetime.fromisoformat(last_export[0])
    if datetime.now() - last_time > timedelta(days=2):
        send_alert(f"Last export was {last_time}, over 2 days ago")
        
    # Check library health trends
    stats = db.calculate_library_stats("radarr")
    if stats.avg_score < -50:
        send_alert(f"Library health declining: avg score {stats.avg_score}")
        
def send_alert(message):
    """Send alert via webhook/email/etc."""
    requests.post("https://hooks.slack.com/webhook", json={
        "text": f"🚨 Arr Score Exporter Alert: {message}"
    })

if __name__ == "__main__":
    check_export_health()
```

## CLI Command Reference

### Complete Command List
```bash
# Core export commands
arr-export radarr                    # Export Radarr with full analysis
arr-export sonarr                    # Export Sonarr with full analysis  
arr-export both                      # Export both services

# Configuration and testing
arr-export test-config               # Test all configurations
arr-export validate-db               # Validate database integrity

# Advanced options
arr-export radarr --config custom.yaml         # Custom config file
arr-export radarr --output-dir /path/exports    # Custom output directory
arr-export radarr --verbose                     # Detailed logging output
arr-export radarr --no-dashboard                # Skip dashboard generation
arr-export radarr --max-workers 3               # Override worker count

# Windows launcher alternatives
python run_enhanced.py radarr                   # Windows-friendly launcher
python run_enhanced.py test-config              # Test with launcher

# Legacy script compatibility
python arr_score_exporter.py radarr --config config.yaml    # Main script
python legacy/export_radarr_scores.py                       # Original script
```

### Exit Codes
- `0`: Success
- `1`: Configuration error
- `2`: API connection error  
- `3`: Database error
- `4`: Export processing error
- `5`: Analysis generation error

### Output Files
All exports create timestamped files:
- `{service}_export_YYYYMMDD_HHMMSS.csv`: Detailed data export
- `{service}_dashboard_YYYYMMDD_HHMMSS.html`: Interactive dashboard
- `export_summary_YYYYMMDD_HHMMSS.txt`: Processing summary
- Database updates in `~/.arr-score-exporter/library.db`