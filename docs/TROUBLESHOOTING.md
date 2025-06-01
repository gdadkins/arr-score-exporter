# Troubleshooting Guide

Quick solutions for common issues with the *Arr Custom Format Score Exporter.

## Quick Diagnostics

```bash
# Test everything
arr-export-enhanced validate-config

# Detailed logging
arr-export-enhanced radarr --verbose

# Check database health
sqlite3 ~/.arr-score-exporter/library.db "PRAGMA integrity_check;"
```

**Status**: **FIXED** in v2.0 with enhanced connection management and WAL mode.

If you still see this error:
1. Ensure you're using the enhanced CLI: `arr-export-enhanced`
2. Check write permissions: `ls -la ~/.arr-score-exporter/`
3. Reset database if needed: `rm ~/.arr-score-exporter/library.db`

## Configuration Issues

### "No configuration file found"
```bash
# Solution: Create configuration file
cp config.yaml.example config.yaml
# Edit config.yaml with your details
```

### "Failed to load configuration"
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Test configuration
arr-export test-config
```

### Invalid YAML syntax
- Use spaces, not tabs for indentation
- Check quotes and colons are properly formatted
- Validate at https://yamlchecker.com/

## API Connection Issues

### "Connection refused" / "401 Unauthorized"
```bash
# Test API manually
curl "http://192.168.1.100:7878/api/v3/system/status" \
     -H "X-Api-Key: YOUR_KEY"

# Get API key from: Settings → General → Security → API Key
```

**Common causes:**
- Wrong URL (check IP address and port)
- Incorrect API key (copy exactly, no extra spaces)
- Radarr/Sonarr not running
- Firewall blocking connection

### "Request failed after retries"
**Performance tuning for unreliable connections:**
```yaml
export:
  max_workers: 3          # Reduce concurrent load
  retry_attempts: 5       # More retries
  retry_delay: 2          # Longer delay between retries
  timeout: 60             # Increase timeout
```

## Performance Issues

### "High memory usage" / "Process killed"
```bash
# Monitor memory usage
top -p $(pgrep -f arr-export)

# Reduce memory usage
```
```yaml
export:
  max_workers: 2          # Reduce from default 5
```

**System requirements:**
- Small libraries (<1000 files): 2GB RAM
- Medium libraries (1000-5000 files): 4GB RAM  
- Large libraries (5000+ files): 8GB+ RAM

### "Export takes too long"
```bash
# Monitor progress with verbose output
arr-export --verbose radarr

# Performance tuning for large libraries
```
```yaml
export:
  max_workers: 3          # Reduce concurrent requests
  timeout: 60             # Increase timeout
```

## Installation Issues

### "ModuleNotFoundError: No module named 'click'"
```bash
# Complete installation
pip install -e .[dev]

# Or install base requirements
pip install -r requirements.txt
```

### "Command not found: arr-export"
```bash
# Check installation
pip show arr-score-exporter

# Use Python module directly
python -m arr_score_exporter.cli --help

# Windows launcher
python run_enhanced.py radarr
```

### Virtual environment issues
```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS  
source venv/bin/activate

# Install in virtual environment
pip install -e .
```

## Data and Analysis Issues

### "No external IDs found"
**Message**: `DEBUG: No external IDs for movie: Some Movie Title`

**Normal behavior** - Some items may not have TMDb/IMDb IDs. Solutions:
1. Check items have proper IDs in Radarr/Sonarr
2. Use "Search for Movie/Series" to improve matching
3. Manually assign IDs for problematic items

### Dashboard sections empty

**Custom format effectiveness empty:**
- Ensure TRaSH Guides custom formats are imported
- Check custom formats are assigned to quality profiles

**Score trends empty:**
- Normal on first run - requires historical data
- Run exports regularly to build trend data

### HTML Report Issues

**Charts not displaying / JavaScript errors:**
```bash
# Regenerate reports with latest fixes
arr-export-enhanced report --service radarr

# Check browser console (F12) for errors
# Should NOT see "dashboardData already declared" error
```

**Interactive features broken (pagination, search, export):**
- **Status**: Fixed in latest version
- **Solution**: Regenerate reports - all Bootstrap 5 dependencies now included
- **Verification**: Look for "Copy CSV", pagination controls, and working tooltips

**Old reports still broken:**
- Delete old HTML files and regenerate
- New reports have full Bootstrap 5 + DataTables + Chart.js integration
- All color coding (red/green/grey) and interactivity restored

### Analysis results seem incorrect
1. Verify TRaSH Guides custom formats are properly configured
2. Check format scores match your preferences
3. Compare dashboard results with known file quality

## Platform-Specific Issues

### Windows Issues

**PowerShell execution policy:**
```powershell
# Allow script execution (as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Use Python directly
python run_enhanced.py radarr
```

**Path length limitations:**
- Enable long path support in Windows 10/11
- Use shorter directory paths
- Run from C:\arr-score-exporter

### Linux/macOS Issues

**Permission denied:**
```bash
# Fix file permissions
chmod +x /usr/local/bin/arr-export

# Fix directory permissions  
chmod 755 ~/.arr-score-exporter

# Use user installation
pip install --user -e .
```

## Emergency Recovery

### Complete system reset
```bash
# 1. Backup important data
cp config.yaml config.yaml.backup
cp -r ~/.arr-score-exporter ~/.arr-score-exporter.backup

# 2. Clean installation
pip uninstall arr-score-exporter
rm -rf ~/.arr-score-exporter

# 3. Fresh installation
pip install -e .

# 4. Restore configuration
cp config.yaml.backup config.yaml

# 5. Test installation
arr-export test-config
```

### Database recovery
```bash
# Check database integrity
sqlite3 ~/.arr-score-exporter/library.db "PRAGMA integrity_check;"

# Reset corrupted database
rm ~/.arr-score-exporter/library.db
arr-export radarr  # Will recreate database
```

## Getting Help

### Before reporting issues

1. **Run diagnostics:**
   ```bash
   arr-export test-config
   arr-export --verbose radarr > debug.log 2>&1
   ```

2. **Check system info:**
   ```bash
   echo "OS: $(uname -a)"
   echo "Python: $(python --version)"
   pip list | grep -E "(arr|click|rich|requests)"
   ```

3. **Test API connectivity:**
   ```bash
   curl "http://192.168.1.100:7878/api/v3/system/status" \
        -H "X-Api-Key: YOUR_KEY"
   ```

### Issue report template

```markdown
## Environment
- OS: [Windows 11 / Ubuntu 22.04 / macOS 13.0]
- Python: [3.11.2]
- Radarr: [4.0.0] at [http://192.168.1.100:7878]
- Library Size: [~3,000 movies]

## Issue
[Clear description of the problem]

## Steps to reproduce
1. Run: `arr-export radarr`
2. Error occurs after processing ~100 files

## Diagnostic output
```
$ arr-export test-config
[Paste output here]

$ arr-export --verbose radarr 2>&1 | tail -50
[Paste relevant log output here]
```

## Attempted solutions
- [x] Verified configuration syntax
- [x] Tested API connectivity manually
- [ ] Tried with reduced max_workers
```

### Support channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and configuration help
- **Documentation**: This guide and API reference

## Performance Baselines

Typical performance metrics for reference:
- **Processing Speed**: 50-100 files/minute
- **Memory Usage**: 100-300MB for typical libraries  
- **API Response Time**: 200-500ms per request
- **Database Operations**: <1ms per file for storage

If your performance differs significantly, include performance metrics in issue reports.