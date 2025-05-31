# Enhanced Troubleshooting Guide

## Common Issues and Solutions

### 🚨 Recently Fixed Issues

#### Database Locking Issues (RESOLVED ✅)
```
sqlite3.OperationalError: database is locked
Error storing media file: database is locked
```

**Status**: **FIXED** in enhanced version

**Solution Implemented**:
- Enhanced connection management with WAL (Write-Ahead Logging) mode
- Thread-safe database operations with proper locking
- Retry logic with exponential backoff for transient lock issues
- Connection pooling and timeout management

**If you still see this error**:
1. Ensure you're using the enhanced CLI: `arr-export radarr`
2. Check that no other processes are accessing the database
3. Verify write permissions to the database directory

#### Custom Format Analysis Empty Results (RESOLVED ✅)
```
Custom format effectiveness showing no results or all zeros
```

**Status**: **FIXED** in enhanced version

**Solution Implemented**:
- Fixed correlation analysis logic to use file total scores instead of individual format scores
- Improved data aggregation for meaningful insights
- Enhanced statistical analysis for format effectiveness

**Verification**: The dashboard now shows meaningful custom format effectiveness data with proper correlation scores.

## Configuration Issues

#### Issue: "No configuration file found"
```
FileNotFoundError: No configuration file found. Please create config.yaml from config.yaml.example
```

**Solution:**
1. Copy the example configuration:
   ```bash
   cp config.yaml.example config.yaml
   # Windows:
   copy config.yaml.example config.yaml
   ```
2. Edit `config.yaml` with your actual API keys and URLs
3. Test configuration: `arr-export test-config`

#### Issue: "Failed to load configuration"
```
RuntimeError: Failed to load configuration: ...
```

**Enhanced Solutions:**
- **YAML Validation**: Use `arr-export test-config` for detailed validation
- **Syntax Checking**: Check YAML syntax using an online validator
- **Indentation**: Ensure proper indentation (use spaces, not tabs)
- **File Encoding**: Verify file encoding is UTF-8
- **Permissions**: Check file read permissions
- **Environment Variables**: Test with environment variable overrides:
  ```bash
  export RADARR_URL="http://localhost:7878"
  export RADARR_API_KEY="your_key_here"
  arr-export test-config
  ```

## Enhanced API Connection Issues

#### Issue: "Connection test failed"
```
Radarr: Connection test failed: HTTPError 401
API connectivity test failed
```

**Enhanced Diagnostic Solutions:**
1. **Use Enhanced Test Command**:
   ```bash
   arr-export test-config  # Provides detailed diagnostics
   ```

2. **Verify API Key**:
   - Go to Radarr/Sonarr → Settings → General → Security
   - Copy the API Key exactly (no extra spaces)
   - Test with curl:
   ```bash
   curl "http://192.168.1.100:7878/api/v3/system/status" \
        -H "X-Api-Key: YOUR_API_KEY"
   ```

3. **Check URL Format**:
   ```yaml
   radarr:
     url: "http://192.168.1.100:7878"  # No trailing slash, use actual IP
     api_key: "your_key_here"
     enabled: true
   ```

4. **Network Connectivity**:
   ```bash
   # Test basic connectivity
   ping 192.168.1.100
   
   # Test port accessibility
   telnet 192.168.1.100 7878
   # or
   nc -zv 192.168.1.100 7878
   ```

#### Issue: "Request failed after 3 attempts"
```
HTTPError: Request failed after 3 attempts
Connection timeout or network issues
```

**Enhanced Solutions:**
- **Service Status**: Verify Radarr/Sonarr is running and responsive
- **Network Connectivity**: Test network path to the service
- **Firewall Settings**: Check firewall rules and port access
- **Performance Tuning**: Adjust configuration for your environment:
  ```yaml
  export:
    max_workers: 3          # Reduce concurrent load
    retry_attempts: 5       # Increase retry count
    retry_delay: 2          # Increase delay between retries
    timeout: 60             # Increase request timeout
  ```
- **System Resources**: Monitor CPU and memory usage on both client and server
- **Network Analysis**: Use network monitoring tools to identify bottlenecks

## Enhanced Database Issues

#### Issue: "Database is locked" (RESOLVED ✅)
```
sqlite3.OperationalError: database is locked
Error storing media file: database is locked
```

**Status**: **FIXED** in enhanced version with:
- WAL (Write-Ahead Logging) mode for better concurrency
- Thread-safe connection management
- Retry logic with exponential backoff
- Proper connection pooling

**If you still encounter this**:
1. **Check Database Permissions**:
   ```bash
   ls -la ~/.arr-score-exporter/
   # Ensure write permissions on database directory
   ```

2. **Manual Database Check**:
   ```bash
   # Check database integrity
   sqlite3 ~/.arr-score-exporter/library.db "PRAGMA integrity_check;"
   
   # Check database mode
   sqlite3 ~/.arr-score-exporter/library.db "PRAGMA journal_mode;"
   # Should return: wal
   ```

3. **Reset Database** (if corrupted):
   ```bash
   # Backup existing database
   cp ~/.arr-score-exporter/library.db ~/.arr-score-exporter/library.db.backup
   
   # Remove corrupted database (will be recreated)
   rm ~/.arr-score-exporter/library.db
   
   # Re-run export
   arr-export radarr
   ```

#### Issue: "Database schema errors"
```
sqlite3.DatabaseError: no such table: media_files
```

**Solutions:**
1. **Database Initialization**:
   ```bash
   # The enhanced version auto-creates schema
   arr-export test-config  # Initializes database
   ```

2. **Manual Schema Check**:
   ```bash
   sqlite3 ~/.arr-score-exporter/library.db ".tables"
   # Should show: media_files, score_history, library_stats, export_runs
   ```

## Enhanced Performance Issues

#### Issue: "Rate limit exceeded"
```
HTTPError 429: Too Many Requests
API rate limiting detected
```

**Enhanced Solutions:**
- **Automatic Handling**: The enhanced version includes intelligent rate limiting
- **Configuration Tuning**:
  ```yaml
  export:
    max_workers: 2          # Reduce concurrent requests
    retry_delay: 2          # Increase delay between requests
    timeout: 30             # Increase timeout for slower responses
  ```
- **Monitor Progress**: Use `arr-export --verbose radarr` to see rate limiting in action
- **Peak Hours**: Avoid running during peak API usage times

#### Issue: "High memory usage"
```
MemoryError: Unable to allocate memory
System running out of memory
```

**Enhanced Solutions:**
1. **Reduce Workers**: Lower the number of concurrent operations
   ```yaml
   export:
     max_workers: 2  # Reduce from default 5
   ```

2. **Monitor Usage**: Check system resources during export
   ```bash
   # Monitor memory usage in real-time
   top -p $(pgrep -f arr-export)
   
   # Check available memory
   free -h
   ```

3. **System Requirements**:
   - **Minimum**: 2GB RAM for libraries under 1,000 files
   - **Recommended**: 4GB+ RAM for larger libraries
   - **Large Libraries** (10,000+ files): 8GB+ RAM recommended

#### Issue: "Export takes too long"
```
Export running for hours without completion
```

**Enhanced Solutions:**
1. **Progress Monitoring**: Use verbose mode to see detailed progress
   ```bash
   arr-export --verbose radarr
   ```

2. **Performance Optimization**:
   ```yaml
   export:
     max_workers: 3          # Optimize for your system
     timeout: 30             # Reduce timeout for faster failures
     retry_attempts: 2       # Reduce retry attempts
   ```

3. **System Optimization**:
   - Close unnecessary applications
   - Ensure good network connectivity to *Arr services
   - Run during off-peak hours
   - Consider running on a more powerful system for very large libraries

## Enhanced Installation and Module Issues

#### Issue: "ModuleNotFoundError: No module named 'click'"
```
ModuleNotFoundError: No module named 'click'
ImportError: Missing required dependencies
```

**Enhanced Solutions:**
1. **Complete Installation**:
   ```bash
   # Install with all dependencies
   pip install -e .[dev]
   
   # Or install base requirements
   pip install -r requirements.txt
   ```

2. **Virtual Environment** (Recommended):
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   
   # Install in virtual environment
   pip install -e .[dev]
   ```

3. **Verify Installation**:
   ```bash
   # Test installation
   arr-export --help
   
   # Test specific modules
   python -c "from arr_score_exporter.config import Config; print('✅ Config module loaded')"
   ```

#### Issue: "ImportError: cannot import name 'RadarrExporter'"
```
ImportError: cannot import name 'RadarrExporter' from 'arr_score_exporter'
```

**Enhanced Solutions:**
1. **Clean Reinstall**:
   ```bash
   pip uninstall arr-score-exporter
   pip install -e .
   ```

2. **Check Python Path**:
   ```bash
   python -c "import sys; print('\n'.join(sys.path))"
   # Ensure project directory is in Python path
   ```

3. **Development Mode Installation**:
   ```bash
   # Ensure editable installation
   pip install -e . --force-reinstall
   ```

#### Issue: "Command not found: arr-export"
```
bash: arr-export: command not found
```

**Enhanced Solutions:**
1. **Check Installation**:
   ```bash
   pip show arr-score-exporter
   # Should show package details
   ```

2. **Use Python Module**:
   ```bash
   python -m arr_score_exporter.enhanced_cli --help
   ```

3. **Windows Launcher**:
   ```bash
   # Use the Windows-specific launcher
   python run_enhanced.py radarr
   ```

4. **PATH Issues**:
   ```bash
   # Find where pip installs scripts
   python -m site --user-base
   
   # Add to PATH if needed
   export PATH="$PATH:$(python -m site --user-base)/bin"
   ```

## Enhanced Data and Analysis Issues

#### Issue: "No external IDs found"
```
DEBUG: No external IDs for movie: Some Movie Title
WARNING: Missing TMDb/IMDb IDs for multiple items
```

**Enhanced Analysis:**
- **Expected Behavior**: This is normal for some items in your library
- **Root Causes**: 
  - New releases not yet in external databases
  - Obscure or regional content
  - Metadata matching issues in *Arr applications

**Solutions:**
1. **Check *Arr Metadata**:
   - Verify items have proper TMDb/IMDb IDs in Radarr/Sonarr
   - Use the "Search for Movie/Series" feature to improve matching
   - Manually assign IDs for problematic items

2. **Monitor Impact**:
   ```bash
   # Use verbose mode to see detailed ID matching
   arr-export --verbose radarr
   ```

3. **Metadata Refresh**:
   - In Radarr/Sonarr, select items and "Refresh Metadata"
   - This can improve ID matching for problematic items

#### Issue: "Dashboard sections empty"
```
Custom format effectiveness: No data
Score trends (30 days): No data
```

**Analysis by Section:**

1. **Custom Format Effectiveness** (Should have data):
   - **If Empty**: May indicate custom formats not properly configured
   - **Verification**: Check that TRaSH Guides custom formats are imported
   - **Solution**: Import and configure custom formats in Radarr/Sonarr

2. **Score Trends** (Expected to be empty on first run):
   - **Expected**: Empty on first export run
   - **Reason**: Requires historical data from multiple export runs
   - **Timeline**: Data appears after 2+ export runs over time

3. **Quality Profile Analysis** (Should have data):
   - **If Empty**: May indicate all files use default profile
   - **Verification**: Check quality profile distribution in *Arr applications

#### Issue: "Analysis results seem incorrect"
```
Upgrade candidates showing high-quality files
Format effectiveness showing unexpected results
```

**Enhanced Diagnostics:**
1. **Verify Custom Format Configuration**:
   - Ensure TRaSH Guides custom formats are properly imported
   - Check that format scores are configured correctly
   - Verify quality profile custom format assignments

2. **Database Analysis**:
   ```bash
   # Check score distribution
   python check_scores.py
   
   # Analyze custom format data
   python check_formats.py
   
   # Test analysis algorithms
   python test_analysis.py
   ```

3. **Manual Verification**:
   - Compare dashboard results with known file quality
   - Verify scoring logic matches your quality preferences
   - Check specific files that seem incorrectly categorized

## Advanced Troubleshooting

### Database Recovery Procedures

#### Complete Database Reset
```bash
# 1. Backup existing database
cp ~/.arr-score-exporter/library.db ~/.arr-score-exporter/library.db.backup

# 2. Remove corrupted database
rm ~/.arr-score-exporter/library.db

# 3. Re-initialize with fresh export
arr-export radarr
```

#### Database Analysis and Repair
```bash
# Check database integrity
sqlite3 ~/.arr-score-exporter/library.db "PRAGMA integrity_check;"

# Analyze database statistics
sqlite3 ~/.arr-score-exporter/library.db "ANALYZE; PRAGMA optimize;"

# Check WAL mode status
sqlite3 ~/.arr-score-exporter/library.db "PRAGMA journal_mode;"
```

### Configuration Validation

#### Comprehensive Configuration Test
```bash
# Test all configuration aspects
arr-export test-config

# Test specific service
echo "Testing Radarr connectivity..."
curl -s "http://192.168.1.100:7878/api/v3/system/status" \
     -H "X-Api-Key: YOUR_KEY" | jq

# Validate YAML syntax
python -c "import yaml; print('✅ YAML valid')" 2>/dev/null || echo "❌ YAML syntax error"
```

#### Environment Variable Testing
```bash
# Test with environment variables
export RADARR_URL="http://192.168.1.100:7878"
export RADARR_API_KEY="your_key_here"
export ARR_MAX_WORKERS="2"
export ARR_LOG_LEVEL="DEBUG"

arr-export test-config
```

### Performance Profiling

#### System Resource Monitoring
```bash
# Monitor during export (Linux/macOS)
top -p $(pgrep -f arr-export)

# Monitor network usage
netstat -i

# Check disk I/O
iotop -p $(pgrep -f arr-export)  # Linux
```

#### Export Performance Analysis
```bash
# Time the export process
time arr-export radarr

# Monitor with verbose output
arr-export --verbose radarr > export.log 2>&1

# Analyze log for bottlenecks
grep -E "(ERROR|WARNING|took|seconds)" export.log
```

### System-Specific Issues

#### Windows-Specific Issues

**Issue**: "PowerShell execution policy"
```
Execution of scripts is disabled on this system
```

**Solution**:
```powershell
# Check current execution policy
Get-ExecutionPolicy

# Allow script execution (as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Use Python directly
python run_enhanced.py radarr
```

**Issue**: "Path length limitations"
```
OSError: [Errno 2] No such file or directory
```

**Solution**:
- Enable long path support in Windows 10/11
- Use shorter directory paths
- Consider running from C:\arr-score-exporter

#### Linux/macOS-Specific Issues

**Issue**: "Permission denied"
```
PermissionError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Fix file permissions
chmod +x /usr/local/bin/arr-export

# Fix directory permissions
chmod 755 ~/.arr-score-exporter

# Run with user installation
pip install --user -e .
```

#### Network and Firewall Issues

**Issue**: "Connection refused"
```
ConnectionError: [Errno 111] Connection refused
```

**Solutions**:
1. **Check Service Status**:
   ```bash
   # Check if Radarr is running
   curl http://192.168.1.100:7878
   
   # Check from same machine
   curl http://localhost:7878
   ```

2. **Network Connectivity**:
   ```bash
   # Test network path
   ping 192.168.1.100
   
   # Test port connectivity
   telnet 192.168.1.100 7878
   nc -zv 192.168.1.100 7878
   ```

3. **Firewall Rules**:
   ```bash
   # Linux - check iptables
   sudo iptables -L
   
   # Check for blocked ports
   sudo netstat -tulpn | grep :7878
   ```

### Logging and Debugging

#### Enable Comprehensive Logging
```bash
# Maximum verbosity
arr-export --verbose radarr 2>&1 | tee debug.log

# Analyze log patterns
grep -E "(ERROR|CRITICAL)" debug.log
grep -E "(database|sqlite)" debug.log
grep -E "(API|HTTP)" debug.log
```

#### Debug Configuration Issues
```bash
# Test configuration loading
python -c "
from arr_score_exporter.config import Config
try:
    config = Config()
    print('✅ Config loaded successfully')
    print(f'Radarr URL: {config.radarr_url}')
    print(f'Max workers: {config.max_workers}')
except Exception as e:
    print(f'❌ Config error: {e}')
"
```

#### Debug Database Issues
```bash
# Test database connectivity
python -c "
from arr_score_exporter.models import DatabaseManager
try:
    db = DatabaseManager()
    with db._get_connection() as conn:
        result = conn.execute('SELECT COUNT(*) FROM media_files').fetchone()
        print(f'✅ Database accessible: {result[0]} files')
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

#### Debug API Connectivity
```bash
# Test API client
python -c "
from arr_score_exporter.config import Config
from arr_score_exporter.api_client import ArrApiClient
try:
    config = Config()
    client = ArrApiClient(config.radarr_url, config.radarr_api_key)
    status = client.get('/system/status')
    print(f'✅ API connected: {status.get(\"appName\", \"Unknown\")} v{status.get(\"version\", \"Unknown\")}')
except Exception as e:
    print(f'❌ API error: {e}')
"
```

### Emergency Recovery Procedures

#### Complete System Reset
```bash
# 1. Backup any important data
cp config.yaml config.yaml.backup
cp -r ~/.arr-score-exporter ~/.arr-score-exporter.backup

# 2. Clean installation
pip uninstall arr-score-exporter
rm -rf ~/.arr-score-exporter
git clean -fxd  # If using git repo

# 3. Fresh installation
pip install -e .[dev]

# 4. Restore configuration
cp config.yaml.backup config.yaml

# 5. Test installation
arr-export test-config
```

#### Recovery from Corrupted State
```bash
# Check system state
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Virtual environment: ${VIRTUAL_ENV:-'None'}"

# Check installed packages
pip list | grep -E "(arr|click|rich|requests)"

# Verify file permissions
ls -la ~/.arr-score-exporter/
ls -la config.yaml

# Test basic functionality
python -c "import arr_score_exporter; print('Import successful')"
```

## Enhanced Debugging Steps

### 1. Comprehensive System Check
```bash
# Test all components
arr-export test-config

# Enable maximum verbosity
arr-export --verbose radarr

# Check system resources
echo "System resources:"
echo "  Memory: $(free -h | grep '^Mem:' | awk '{print $3"/"$2}')"
echo "  Disk: $(df -h ~ | tail -1 | awk '{print $3"/"$2" ("$5" used)"}')"
echo "  Python: $(python --version)"
```

### 2. Component-by-Component Testing
```bash
# Test configuration loading
echo "Testing configuration..."
python -c "from arr_score_exporter.config import Config; Config(); print('✅ Config OK')"

# Test database
echo "Testing database..."
python -c "from arr_score_exporter.models import DatabaseManager; DatabaseManager(); print('✅ Database OK')"

# Test API connectivity
echo "Testing API..."
arr-export test-config
```

### 3. Manual API Verification
```bash
# Test Radarr API with detailed output
echo "Testing Radarr API..."
curl -v "http://192.168.1.100:7878/api/v3/system/status" \
     -H "X-Api-Key: YOUR_KEY" \
     -H "Content-Type: application/json"

# Test with specific endpoints
curl "http://192.168.1.100:7878/api/v3/movie?pageSize=1" \
     -H "X-Api-Key: YOUR_KEY" | jq

# Test quality profiles
curl "http://192.168.1.100:7878/api/v3/qualityprofile" \
     -H "X-Api-Key: YOUR_KEY" | jq
```

### 4. Performance Analysis
```bash
# Monitor export performance
time arr-export --verbose radarr

# Check for bottlenecks
strace -e trace=network,file arr-export radarr 2>&1 | head -100

# Monitor system resources during export
(arr-export radarr &); top -p $!
```

## Enhanced Log Analysis

### Understanding Enhanced Log Levels

- **DEBUG**: Detailed processing, API calls, database operations
- **INFO**: Progress updates, summaries, and completion status
- **WARNING**: Non-fatal issues that don't stop processing
- **ERROR**: Serious issues requiring attention
- **CRITICAL**: Fatal errors that stop execution

### Enhanced Log Message Categories

#### Normal Operation (Enhanced)
```
🚀 Starting Radarr export with enhanced analysis...
📊 Found 3,231 movies in Radarr
💾 Database: ~/.arr-score-exporter/library.db (WAL mode)
⚡ Processing with 5 workers...
📈 Export complete: 3,231 processed, 3,015 stored, 0 errors
🎯 Analysis complete: 1,252 upgrade candidates identified
📊 Dashboard generated: exports/radarr_dashboard_20241129_143022.html
✅ Export successful in 45.2 seconds
```

#### Expected Warnings (Enhanced)
```
⚠️  No external IDs for movie: Some Obscure Film (2023)
⚠️  Custom format data empty for: Another Movie
⚠️  Rate limiting detected - backing off for 2.5 seconds
⚠️  Database busy - retrying in 0.1 seconds (attempt 1/3)
```

#### Concerning Errors (Enhanced)
```
❌ Failed to get movie details for ID 123: HTTP 404 Not Found
❌ Database error: PRAGMA journal_mode failed
❌ API connection failed after 3 attempts: Connection timeout
❌ Error storing media file: unique constraint failed
```

#### Performance Indicators
```
📊 API calls: 3,231 total, 95.2 req/min average
💾 Database: 3,015 inserts, 156 updates, 0 conflicts
⏱️  Processing time: 45.2s total, 0.014s/file average
🧠 Memory usage: 234MB peak, 156MB average
```

### Log Analysis Commands
```bash
# Extract performance metrics
grep -E "(processing|completed|seconds|req/min)" export.log

# Find errors and warnings
grep -E "(ERROR|WARNING|❌|⚠️)" export.log

# Analyze database operations
grep -E "(database|sqlite|💾)" export.log

# Check API performance
grep -E "(API|HTTP|rate limit|🌐)" export.log

# View summary statistics
tail -20 export.log | grep -E "(✅|📊|📈)"
```

## Enhanced Performance Optimization

### Configuration Tuning for Different Scenarios

#### Large Libraries (5,000+ files)
```yaml
export:
  max_workers: 3              # Reduce to prevent overwhelming
  retry_attempts: 5           # Increase for reliability
  retry_delay: 1              # Moderate delay
  timeout: 60                 # Increase timeout
  
dashboard:
  show_upgrade_candidates: 50 # Show more candidates
  show_format_analysis: 25    # More detailed analysis
```

#### Fast Networks / Powerful Systems
```yaml
export:
  max_workers: 8              # Increase parallelism
  retry_attempts: 3           # Standard retry count
  retry_delay: 0.5            # Faster retry
  timeout: 30                 # Standard timeout
```

#### Limited Resources / Slow Networks
```yaml
export:
  max_workers: 2              # Minimal parallelism
  retry_attempts: 5           # More retries for unreliable connections
  retry_delay: 2              # Longer delay
  timeout: 120                # Extended timeout
```

#### Development / Testing
```yaml
export:
  max_workers: 1              # Single-threaded for debugging
  retry_attempts: 1           # Fail fast for testing
  retry_delay: 0.1            # Minimal delay
  timeout: 10                 # Quick timeout
  
logging:
  level: "DEBUG"              # Maximum verbosity
  console_output: true        # Show all output
```

### Enhanced System Requirements

#### Minimum Configuration
- **RAM**: 2GB (libraries under 1,000 files)
- **CPU**: 1 core, 2+ GHz
- **Storage**: 500MB free space
- **Network**: 1 Mbps stable connection
- **Python**: 3.8+

#### Recommended Configuration
- **RAM**: 4GB (libraries under 5,000 files)
- **CPU**: 2+ cores, 2.5+ GHz
- **Storage**: 1GB free space (for database and exports)
- **Network**: 10+ Mbps stable connection
- **Python**: 3.11+ (best performance)

#### Large Library Configuration (10,000+ files)
- **RAM**: 8GB+
- **CPU**: 4+ cores, 3+ GHz
- **Storage**: 2GB+ free space
- **Network**: 50+ Mbps stable connection
- **Python**: 3.11+ with optimizations

### Performance Monitoring
```bash
# Monitor system resources during export
htop -p $(pgrep -f arr-export)

# Check network usage
iftop -i eth0  # Replace with your network interface

# Monitor disk I/O
iotop -a -o

# Check database performance
time sqlite3 ~/.arr-score-exporter/library.db "SELECT COUNT(*) FROM media_files;"
```

## Getting Help and Support

### Before Reporting Issues

#### Essential Diagnostic Steps
1. **Run Enhanced Diagnostics**:
   ```bash
   arr-export test-config      # Comprehensive system test
   arr-export --verbose radarr # Detailed logging
   ```

2. **Collect System Information**:
   ```bash
   echo "System Information:"
   echo "  OS: $(uname -a)"
   echo "  Python: $(python --version)"
   echo "  Pip packages:"
   pip list | grep -E "(arr|click|rich|requests|sqlite)"
   ```

3. **Check Configuration**:
   ```bash
   # Verify configuration syntax
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   
   # Test API connectivity
   curl -s "http://192.168.1.100:7878/api/v3/system/status" \
        -H "X-Api-Key: YOUR_KEY" | jq .appName
   ```

4. **Database Health Check**:
   ```bash
   # Check database integrity
   sqlite3 ~/.arr-score-exporter/library.db "PRAGMA integrity_check;"
   
   # Check record counts
   sqlite3 ~/.arr-score-exporter/library.db \
           "SELECT 'media_files', COUNT(*) FROM media_files;"
   ```

### Enhanced Issue Report Template

```markdown
# Issue Report: [Brief Description]

## Environment Information
**System:**
- OS: [Windows 11 / Ubuntu 22.04 / macOS 13.0]
- Architecture: [x64 / ARM64]
- Python Version: [3.11.2]
- Package Version: [Enhanced v2.0]

**Arr Applications:**
- Radarr Version: [4.0.0] at [http://192.168.1.100:7878]
- Sonarr Version: [3.0.0] at [http://192.168.1.100:8989]
- Library Size: [~3,000 movies, ~500 series]

**Configuration:**
```yaml
# Relevant parts of config.yaml
export:
  max_workers: 5
  output_dir: "exports"
```

## Issue Description
[Clear description of the problem]

## Steps to Reproduce
1. Run: `arr-export radarr`
2. Error occurs after processing ~100 files
3. [Additional steps]

## Expected vs Actual Behavior
**Expected:** [What should happen]
**Actual:** [What actually happens]

## Diagnostic Output

### Configuration Test
```
$ arr-export test-config
[Paste output here]
```

### Error Logs
```
$ arr-export --verbose radarr 2>&1 | tail -50
[Paste relevant log output here]
```

### System Status
```
$ python check_scores.py
[Paste database analysis if relevant]
```

## Attempted Solutions
- [x] Verified configuration syntax
- [x] Tested API connectivity manually
- [x] Checked database integrity
- [ ] Tried with reduced max_workers
- [ ] Tested with fresh database

## Additional Context
[Any other relevant information]
```

### Community Support Resources

#### Primary Support Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions, configuration help, and usage tips
- **Documentation**: Comprehensive guides and troubleshooting

#### Self-Help Resources
- **Quick Tests**: Use `python test_quick.py` for rapid validation
- **Analysis Tests**: Use `python test_analysis.py` for analysis validation
- **Database Tools**: Use `python check_scores.py` and `python check_formats.py`

#### Expert-Level Debugging
```bash
# Enable SQLite debugging
export SQLITE_DEBUG=1
arr-export --verbose radarr

# Profile performance
python -m cProfile -o profile.stats -m arr_score_exporter.enhanced_cli radarr
python -m pstats profile.stats

# Memory profiling
python -m memory_profiler -m arr_score_exporter.enhanced_cli radarr

# Network debugging
WIRESHARK_CAPTURE=1 arr-export radarr  # If Wireshark available
```

### Escalation Path

1. **Level 1**: Check this troubleshooting guide
2. **Level 2**: Run diagnostic commands and test basic fixes
3. **Level 3**: Create detailed issue report with full diagnostics
4. **Level 4**: Provide additional debugging output if requested
5. **Level 5**: Collaborate on fixes and testing

### Performance Baseline

For reference, typical performance metrics:
- **Processing Speed**: 50-100 files/minute (depends on system and network)
- **Memory Usage**: 100-300MB for typical libraries
- **Database Operations**: <1ms per file for storage
- **API Response Time**: 200-500ms per request to *Arr services

If your performance significantly differs from these baselines, include performance metrics in your issue report.