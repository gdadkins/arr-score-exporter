# Comprehensive Usage Guide

This guide provides detailed information about using the *Arr Custom Format Score Exporter v2.0 with intelligent analysis and interactive dashboards.

## 📋 Table of Contents

- [Getting Started](#-getting-started)
- [Configuration](#️-configuration)
- [Basic Usage](#-basic-usage)
- [Advanced Features](#-advanced-features)
- [Dashboard Guide](#-dashboard-guide)
- [Analysis Interpretation](#-analysis-interpretation)
- [Performance Optimization](#️-performance-optimization)
- [Troubleshooting](#-troubleshooting)

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:

1. **Python 3.8+** installed (Python 3.11+ recommended)
2. **Radarr v4+** and/or **Sonarr v3+** running and accessible
3. **TRaSH Guides Custom Formats** configured in your *Arr applications
4. **API Keys** from your Radarr/Sonarr instances

### Quick Installation

```bash
# Clone and install
git clone https://github.com/gdadkins/arr-score-exporter.git
cd arr-score-exporter
pip install -e .

# Configure
cp config.yaml.example config.yaml
# Edit config.yaml with your details

# Test
arr-export test-config
```

## ⚙️ Configuration

### Basic Configuration

Create your `config.yaml` file:

```yaml
# Radarr Configuration
radarr:
  url: "http://192.168.1.100:7878"
  api_key: "your_radarr_api_key_here"
  enabled: true

# Sonarr Configuration
sonarr:
  url: "http://192.168.1.100:8989"
  api_key: "your_sonarr_api_key_here"
  enabled: true

# Export Settings
export:
  max_workers: 5
  output_dir: "exports"
  generate_dashboard: true
```

### Advanced Configuration

```yaml
# Complete configuration with all options
radarr:
  url: "http://192.168.1.100:7878"
  api_key: "your_radarr_api_key_here"
  enabled: true

sonarr:
  url: "http://192.168.1.100:8989"
  api_key: "your_sonarr_api_key_here"
  enabled: true

export:
  # Performance settings
  max_workers: 5              # Parallel API calls (2-8 recommended)
  retry_attempts: 3           # API retry count for failed requests
  retry_delay: 1              # Delay between retries (seconds)
  timeout: 30                 # Request timeout (seconds)
  
  # Output settings
  output_dir: "exports"       # Directory for generated files
  generate_dashboard: true    # Create HTML dashboard
  
  # Database settings
  database_path: "~/.arr-score-exporter/library.db"
  
  # Analysis settings
  upgrade_candidate_threshold: -50  # Score threshold for upgrade candidates
  enable_trend_analysis: true       # Track changes over time

# Dashboard customization (optional)
dashboard:
  title: "My Media Library Analysis"
  theme: "light"              # light or dark
  show_upgrade_candidates: 20 # Number of candidates to display
  show_format_analysis: 15    # Number of formats to analyze

# Logging (optional)
logging:
  level: "INFO"              # DEBUG, INFO, WARNING, ERROR
  file: "arr-exporter.log"   # Log file path
  console_output: true       # Show logs in terminal
```

### Environment Variable Override

You can override any configuration value with environment variables:

```bash
# Service configuration
export RADARR_URL="http://localhost:7878"
export RADARR_API_KEY="your_key_here"
export SONARR_URL="http://localhost:8989"
export SONARR_API_KEY="your_key_here"

# Performance tuning
export ARR_MAX_WORKERS="3"
export ARR_RETRY_ATTEMPTS="5"
export ARR_OUTPUT_DIR="/data/exports"

# Dashboard settings
export ARR_DASHBOARD_THEME="dark"
export ARR_DASHBOARD_TITLE="Production Library"
```

## 📋 Basic Usage

### Essential Commands

```bash
# Test configuration and connectivity
arr-export test-config

# Export Radarr data with analysis
arr-export radarr

# Export Sonarr data with analysis
arr-export sonarr

# Export both services
arr-export both
```

### Command Options

```bash
# Verbose output for debugging
arr-export --verbose radarr

# Custom configuration file
arr-export --config /path/to/config.yaml radarr

# Custom output directory
arr-export --output-dir /custom/path radarr

# Help and version info
arr-export --help
arr-export --version
```

### Understanding Output

When you run an export, you'll see:

```
🚀 Starting Radarr export...

📋 Configuration:
  ✅ Radarr: http://192.168.1.100:7878 (3,231 movies)
  💾 Database: ~/.arr-score-exporter/library.db
  ⚙️ Workers: 5 parallel threads

🔄 Processing: ████████████████████ 100% 3,231/3,231

📊 Analysis Results:
  🎯 Upgrade candidates: 1,252 files identified
  🔍 Library health: B+ (78.5/100)
  📊 Dashboard: exports/radarr_dashboard_20241129.html
  📄 CSV Export: exports/radarr_export_20241129.csv

✅ Export completed in 45.2 seconds
```

## 🌟 Advanced Features

### Historical Tracking

The enhanced version automatically tracks changes over time:

- **Score Changes**: Monitors when file scores change
- **Library Trends**: Tracks overall library health improvements
- **Upgrade Tracking**: Records when files are upgraded
- **Format Adoption**: Monitors new custom format usage

### Intelligent Analysis

#### Upgrade Candidate Detection

The system identifies files that would benefit from upgrades based on:

1. **Score Threshold**: Files below your configured threshold
2. **Negative Formats**: Files with formats that subtract points
3. **Missing High-Value Formats**: Files lacking beneficial formats
4. **Quality Inconsistencies**: Files that don't match profile expectations

#### Custom Format Effectiveness

Analyzes which TRaSH Guides formats provide the most value:

- **Usage Frequency**: How often each format appears
- **Score Contribution**: Average score impact per format
- **ROI Analysis**: Value vs. storage cost for each format
- **Optimization Recommendations**: Suggestions for format configuration

#### Quality Profile Performance

Compares your quality profiles:

- **Score Distribution**: How files perform within each profile
- **Effectiveness Rating**: A-F grades for each profile
- **Usage Statistics**: Which profiles are most/least used
- **Optimization Suggestions**: Recommendations for profile improvements

### Database Features

The SQLite database provides:

```bash
# Check database status
sqlite3 ~/.arr-score-exporter/library.db "SELECT COUNT(*) FROM media_files;"

# View recent changes
sqlite3 ~/.arr-score-exporter/library.db "
  SELECT timestamp, change_type, file_id, old_score, new_score 
  FROM score_history 
  ORDER BY timestamp DESC 
  LIMIT 10;
"

# Library statistics
sqlite3 ~/.arr-score-exporter/library.db "
  SELECT 
    service_type,
    COUNT(*) as total_files,
    AVG(total_score) as avg_score,
    MIN(total_score) as min_score,
    MAX(total_score) as max_score
  FROM media_files 
  GROUP BY service_type;
"
```

## 🎨 Dashboard Guide

### Dashboard Sections

The interactive HTML dashboard includes:

#### 1. Library Overview
- **Health Score**: Overall library quality (0-100)
- **Health Grade**: Letter grade (A-F) with color coding
- **File Counts**: Total files and distributions
- **Score Statistics**: Min, max, average, and median scores

#### 2. Upgrade Candidates
- **Priority Ranking**: 1=Critical, 2=High, 3=Medium, 4=Low
- **Specific Recommendations**: Exactly what to look for
- **Potential Score Gains**: Expected improvement from upgrades
- **File Details**: Complete metadata for each candidate

#### 3. Custom Format Analysis
- **Effectiveness Charts**: Visual representation of format value
- **Usage Statistics**: How frequently each format is used
- **Score Contribution**: Average score impact per format
- **Optimization Tips**: Recommendations for format configuration

#### 4. Quality Profile Performance
- **Comparative Analysis**: Side-by-side profile comparison
- **Score Distributions**: How files perform in each profile
- **Usage Patterns**: Which profiles are most effective
- **Recommendations**: Suggestions for profile optimization

#### 5. Score Trends (Historical)
- **Change Over Time**: Visual trends showing improvements
- **Upgrade Activity**: When and how many files were improved
- **Health Progression**: Library health improvements over time
- **Format Adoption**: New format usage patterns

### Dashboard Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Charts**: Click and hover for detailed information
- **Export Functionality**: Save data as CSV directly from dashboard
- **Print Friendly**: Optimized layouts for printing reports
- **Accessibility**: Screen reader compatible with proper ARIA labels

## 🔍 Analysis Interpretation

### Understanding Scores

**Positive Scores (+):**
- Indicate desirable qualities (Remux, HDR, high bitrates)
- Higher positive scores = better quality

**Negative Scores (-):**
- Indicate undesirable qualities (Cam, TS, low quality)
- More negative scores = lower quality

**Zero Scores (0):**
- Neutral or unmatched formats
- Common for standard releases

### Priority Levels

**Priority 1 (Critical):**
- Files with significantly negative scores
- Immediate attention recommended
- Often containing harmful formats (Cam, TS)

**Priority 2 (High):**
- Files well below library average
- Should be upgraded when possible
- Missing key quality indicators

**Priority 3 (Medium):**
- Files slightly below optimal
- Upgrade when convenient
- Minor quality improvements available

**Priority 4 (Low):**
- Files near or above average
- Upgrade only if storage allows
- Minimal quality improvements

### Health Grades

- **A (90-100)**: Excellent library with mostly high-quality files
- **B (80-89)**: Good library with some optimization opportunities
- **C (70-79)**: Average library needing moderate improvements
- **D (60-69)**: Below average library requiring attention
- **F (<60)**: Poor library needing significant improvements

## ⚙️ Performance Optimization

### System-Specific Tuning

**Small Libraries (<1,000 files):**
```yaml
export:
  max_workers: 3
  retry_attempts: 3
  timeout: 30
```

**Medium Libraries (1,000-5,000 files):**
```yaml
export:
  max_workers: 5
  retry_attempts: 3
  timeout: 45
```

**Large Libraries (5,000+ files):**
```yaml
export:
  max_workers: 3          # Reduce to avoid overwhelming *Arr
  retry_attempts: 5       # More retries for reliability
  timeout: 60             # Longer timeout for large requests
```

**Fast Systems/Networks:**
```yaml
export:
  max_workers: 8          # Increase parallelism
  retry_delay: 0.5        # Faster retry cycles
  timeout: 20             # Shorter timeout for fast responses
```

### Memory Management

Monitor memory usage during exports:

```bash
# Monitor memory usage (Linux/macOS)
top -p $(pgrep -f arr-export)

# Check available memory
free -h

# Windows Task Manager or PowerShell
Get-Process -Name python | Select-Object ProcessName, WorkingSet
```

If experiencing memory issues:
1. Reduce `max_workers` to 2-3
2. Close other applications during export
3. Consider upgrading system RAM
4. Run exports during off-peak hours

### Network Optimization

For slow or unreliable networks:

```yaml
export:
  max_workers: 2          # Reduce concurrent requests
  retry_attempts: 5       # More retries for reliability
  retry_delay: 2          # Longer delays between retries
  timeout: 120            # Extended timeout for slow responses
```

## 🚑 Troubleshooting

### Common Issues and Solutions

#### Configuration Issues

**"No configuration file found"**
```bash
# Solution: Create configuration file
cp config.yaml.example config.yaml
# Edit config.yaml with your details
```

**"Invalid YAML syntax"**
```bash
# Solution: Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

#### Connection Issues

**"Connection refused"**
1. Verify *Arr services are running
2. Check URLs in configuration
3. Test manual connection:
```bash
curl "http://your-radarr:7878/api/v3/system/status" -H "X-Api-Key: YOUR_KEY"
```

**"401 Unauthorized"**
1. Verify API key is correct
2. Check API key hasn't expired
3. Ensure no extra spaces in configuration

#### Performance Issues

**"Export taking too long"**
1. Reduce `max_workers` in configuration
2. Check network connectivity to *Arr services
3. Monitor system resources during export

**"High memory usage"**
1. Reduce `max_workers` to 2-3
2. Close other applications
3. Consider system upgrade for large libraries

#### Database Issues

**"Database is locked"** (Fixed in v2.0)
This issue was resolved with enhanced connection management. If you still encounter it:
1. Ensure no other processes are accessing the database
2. Check file permissions on database directory
3. Try restarting the export

### Advanced Diagnostics

#### System Health Check
```bash
# Test everything
arr-export test-config

# Check Python environment
python --version
pip list | grep -E "(click|rich|requests|sqlite)"

# Verify file permissions
ls -la ~/.arr-score-exporter/
ls -la exports/
```

#### Network Diagnostics
```bash
# Test network connectivity
ping your-radarr-hostname
telnet your-radarr-hostname 7878

# Test API endpoints
curl -v "http://your-radarr:7878/api/v3/system/status" -H "X-Api-Key: YOUR_KEY"
```

#### Database Diagnostics
```bash
# Check database integrity
sqlite3 ~/.arr-score-exporter/library.db "PRAGMA integrity_check;"

# Check database size and tables
ls -lh ~/.arr-score-exporter/library.db
sqlite3 ~/.arr-score-exporter/library.db ".tables"

# Check record counts
sqlite3 ~/.arr-score-exporter/library.db "
  SELECT 
    'media_files' as table_name, COUNT(*) as records 
  FROM media_files
  UNION ALL
  SELECT 
    'score_history' as table_name, COUNT(*) as records 
  FROM score_history
  UNION ALL
  SELECT 
    'export_runs' as table_name, COUNT(*) as records 
  FROM export_runs;
"
```

### Getting Help

If you continue to experience issues:

1. **Enable verbose logging**:
   ```bash
   arr-export --verbose radarr > debug.log 2>&1
   ```

2. **Check the troubleshooting guide**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

3. **Create an issue** on GitHub with:
   - Your configuration (remove API keys)
   - Error messages
   - System information
   - Debug log output

## 🎯 Best Practices

### Regular Maintenance

1. **Weekly Exports**: Run exports weekly to track improvements
2. **Monitor Trends**: Check dashboard trends for library health
3. **Database Cleanup**: Occasionally check database size and clean old data
4. **Configuration Updates**: Keep TRaSH Guides formats updated

### Optimization Workflow

1. **Initial Export**: Get baseline library health score
2. **Identify Priorities**: Focus on Priority 1 and 2 upgrade candidates
3. **Implement Changes**: Upgrade files or adjust quality profiles
4. **Track Progress**: Run regular exports to monitor improvements
5. **Fine-tune**: Adjust custom format scores based on analysis

### Production Deployment

For automated environments:

```bash
# Cron job for daily exports
0 2 * * * cd /path/to/arr-score-exporter && arr-export both

# Docker deployment
docker run -v /config:/config -v /data:/data arr-score-exporter:latest arr-export both

# Kubernetes CronJob
# See docs/API_REFERENCE.md for complete Kubernetes examples
```

This comprehensive guide covers all aspects of using the *Arr Custom Format Score Exporter v2.0. For additional technical details, see the [API Reference](docs/API_REFERENCE.md) and [Architecture Guide](docs/ARCHITECTURE.md).