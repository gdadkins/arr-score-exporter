# Usage Guide

Detailed examples and workflows for the *Arr Custom Format Score Exporter.

## ⚠️ Important: Data Collection vs Report Generation

**After upgrading files in Radarr/Sonarr, upgrade opportunities won't update until you refresh the data:**

```bash
# ✅ CORRECT: Refresh data after file upgrades
arr-export-enhanced radarr      # Downloads fresh data from Radarr
arr-export-enhanced sonarr      # Downloads fresh data from Sonarr

# ❌ WRONG: Only reads cached data (outdated after upgrades)  
arr-export-enhanced report --service radarr    # No API calls, uses cached data
arr-export-enhanced report --service sonarr    # No API calls, uses cached data
```

**Key Difference:**
- `arr-export-enhanced radarr/sonarr` = **Fresh data collection** + report generation
- `arr-export-enhanced report --service X` = **Cached data only** + report generation

## Two Export Modes

### 1. Basic CSV Export (`arr-export`)
- Creates CSV files with scoring data
- Simple command-line interface
- Good for data analysis and automation

### 2. Enhanced Analysis (`arr-export-enhanced`)
- Collects data with CSV export
- Creates interactive HTML dashboards with visual charts and export functionality
- File size vs score scatter plots for correlation analysis
- Intelligent upgrade recommendations with priority ranking
- Historical tracking with trend analysis
- Professional UI with Bootstrap 5 integration and responsive design

## Basic Usage Examples

### CSV Export
```bash
# Export Radarr data to CSV
arr-export radarr

# Export with verbose logging
arr-export --verbose radarr

# Custom output directory
arr-export --output-dir /data/exports radarr

# Custom configuration
arr-export --config production.yaml radarr
```

### Enhanced Analysis Workflow

#### Two-Step Process
```bash
# Step 1: Collect fresh data from Radarr (connects to API)
arr-export-enhanced radarr

# Step 2: Generate interactive dashboard from cached data (no API calls)
arr-export-enhanced report --service radarr

# One-time setup: Validate configuration
arr-export-enhanced validate-config
```

#### When to Use Each Command
- **Use `arr-export-enhanced radarr/sonarr`** when:
  - You've upgraded files and want to see updated scores
  - You want fresh data from your Arr applications
  - You need both data collection AND report generation
  
- **Use `arr-export-enhanced report --service radarr/sonarr`** when:
  - You want to regenerate reports from existing data (fast)
  - You want different report settings without re-downloading data
  - You're experimenting with report layouts or limits

## Configuration Examples

### Basic Configuration
```yaml
radarr:
  url: "http://192.168.1.100:7878"
  api_key: "your_api_key_here"
  enabled: true

sonarr:
  url: "http://192.168.1.100:8989"
  api_key: "your_api_key_here"
  enabled: true

export:
  output_dir: "exports"
  max_workers: 5
```

### Performance Tuning for Large Libraries
```yaml
export:
  max_workers: 3          # Reduce for large libraries
  retry_attempts: 5       # More retries for reliability
  timeout: 60             # Longer timeout
  
dashboard:
  show_upgrade_candidates: 50   # Show more candidates
```

## Environment Variable Configuration

```bash
# Override configuration with environment variables
export RADARR_URL="http://localhost:7878"
export RADARR_API_KEY="your_key"
export SONARR_URL="http://localhost:8989"
export SONARR_API_KEY="your_key"
export ARR_MAX_WORKERS="3"
export ARR_OUTPUT_DIR="/data/exports"

# Run with environment config
arr-export radarr
```

## Understanding Dashboard Output

### Library Health Score
- **A (90-100)**: Excellent library quality
- **B (80-89)**: Good with minor issues
- **C (70-79)**: Average quality
- **D (60-69)**: Below average, needs attention
- **F (<60)**: Poor quality, immediate attention needed

**Dashboard Display**: Total library size automatically displays in TB for large collections (>1TB) for better readability.

### Upgrade Candidate Priorities
- **Priority 1**: Critical - Files with harmful formats (Cam, TS)
- **Priority 2**: High - Files well below library average
- **Priority 3**: Medium - Files slightly below optimal
- **Priority 4**: Low - Files near average, minor improvements

### Score Interpretation
- **Positive scores**: Good quality indicators (Remux, HDR, high bitrates)
- **Negative scores**: Poor quality indicators (Cam, TS, low quality)
- **Zero scores**: Neutral or unmatched formats

## Common Workflows

### Weekly Library Health Check
```bash
#!/bin/bash
# weekly_check.sh - Refresh data and generate reports
arr-export test-config
arr-export-enhanced radarr      # Fresh data + report
arr-export-enhanced sonarr      # Fresh data + report
# Results saved with timestamps for tracking improvements
```

### After Upgrading Files (CRITICAL WORKFLOW)
```bash
# You've upgraded movies/episodes and want to see updated scores
arr-export-enhanced radarr      # Gets fresh data from Radarr
arr-export-enhanced sonarr      # Gets fresh data from Sonarr

# Or if you only want to refresh reports from existing data:
arr-export-enhanced report --service radarr
arr-export-enhanced report --service sonarr
```

### Find Upgrade Candidates
1. **First, ensure you have fresh data**: `arr-export-enhanced radarr`
2. Open generated HTML dashboard (or use `arr-export-enhanced report --service radarr` for cached data)
3. Review "Upgrade Candidates" section
4. Focus on Priority 1 and 2 items first
5. Look for specific format recommendations
6. **After upgrading**: Re-run `arr-export-enhanced radarr` to see updated scores

### Track Library Improvements
- Run exports regularly (weekly/monthly)
- Compare health scores over time
- Monitor upgrade candidate count decreasing
- Track format adoption in dashboard

## Automation Examples

### Cron Job for Regular Reports
```bash
# Add to crontab: crontab -e
# Run every Sunday at 2 AM - collect fresh data
0 2 * * 0 cd /path/to/arr-score-exporter && arr-export-enhanced radarr && arr-export-enhanced sonarr
```

### Windows Task Scheduler
- Action: Start program
- Program: `python`
- Arguments: `arr-export-enhanced radarr` (collect fresh data)
- Start in: `C:\path\to\arr-score-exporter`
- Create separate tasks for each service if needed

### Docker Usage
```bash
# Run in Docker container - collect fresh data
docker run -v /config:/config -v /exports:/exports \
  arr-score-exporter:latest \
  arr-export-enhanced radarr

# For report-only generation from cached data
docker run -v /config:/config -v /exports:/exports \
  arr-score-exporter:latest \
  arr-export-enhanced report --service radarr
```

## Performance Tips

### Small Libraries (<1000 files)
```yaml
export:
  max_workers: 5
  timeout: 30
```

### Medium Libraries (1000-5000 files)
```yaml
export:
  max_workers: 5
  timeout: 45
```

### Large Libraries (5000+ files)
```yaml
export:
  max_workers: 3
  retry_attempts: 5
  timeout: 60
```

### System Resource Monitoring
```bash
# Monitor memory usage during export
top -p $(pgrep -f arr-export)

# Check database size
ls -lh ~/.arr-score-exporter/library.db

# Monitor network usage
netstat -i
```

## Troubleshooting Quick Fixes

### Connection Issues
```bash
# Test API connectivity manually
curl "http://192.168.1.100:7878/api/v3/system/status" \
     -H "X-Api-Key: YOUR_KEY"
```

### Configuration Issues
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Test configuration
arr-export test-config
```

### Performance Issues
```bash
# Run with verbose logging
arr-export --verbose radarr > debug.log 2>&1

# Check for bottlenecks
grep -E "(ERROR|WARNING|timeout)" debug.log
```

### Database Issues
```bash
# Check database integrity
sqlite3 ~/.arr-score-exporter/library.db "PRAGMA integrity_check;"

# Reset database if needed
rm ~/.arr-score-exporter/library.db
arr-export radarr  # Will recreate database
```

## Advanced Usage

### Custom Format Analysis
Use the enhanced dashboard to:
1. Identify most/least effective custom formats
2. Find formats that aren't providing value
3. Optimize quality profile scoring
4. Track format adoption over time

### Quality Profile Optimization
1. Compare profiles in dashboard
2. Identify underperforming profiles
3. Review score distribution by profile
4. Adjust custom format assignments

### Historical Trend Analysis
- Run exports regularly to build historical data
- Dashboard shows trends after multiple runs
- Track library health improvements
- Monitor upgrade completion progress

For detailed troubleshooting, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
For technical details, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).