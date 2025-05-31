# *Arr Custom Format Score Exporter

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Release](https://img.shields.io/badge/version-2.0-brightgreen)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

A comprehensive Python tool that connects to your Radarr and Sonarr instances to extract, analyze, and export TRaSH Guides custom format scores. Generate interactive dashboards, identify upgrade candidates, and optimize your media library with intelligent insights.

![Dashboard Preview](https://via.placeholder.com/800x400/2C3E50/ECF0F1?text=Interactive+Dashboard+Preview)
*Interactive HTML dashboard showing library analysis and upgrade recommendations*

## What This Does

This tool connects to your Radarr and Sonarr instances to:

### 🎯 **Smart Analysis**
- **Upgrade Candidate Detection**: Automatically identifies files that would benefit from upgrades
- **Custom Format Effectiveness**: Analyzes which TRaSH Guides formats provide the most value
- **Quality Profile Optimization**: Evaluates and compares your quality profile performance
- **Library Health Scoring**: Overall health assessment with actionable recommendations

### 📊 **Interactive Reporting** 
- **Rich HTML Dashboards**: Beautiful, responsive reports with charts and visualizations
- **Real-time Progress**: Modern CLI with progress bars and status indicators
- **Multiple Export Formats**: CSV, JSON, and database storage options
- **Historical Trend Analysis**: Track improvements and changes over time

### 🔧 **Enterprise Ready**
- **Thread-Safe Database**: SQLite with WAL mode for reliable concurrent access
- **Robust Error Handling**: Comprehensive retry logic and graceful degradation
- **Configurable Performance**: Tunable workers and rate limiting
- **Production Deployment**: Docker support and environment variable configuration

## ⚡ Quick Start

```bash
# 1. Clone and install
git clone https://github.com/gdadkins/arr-score-exporter.git
cd arr-score-exporter
pip install -e .

# 2. Configure
cp config.yaml.example config.yaml
# Edit config.yaml with your Radarr/Sonarr URLs and API keys

# 3. Test connection
arr-export test-config

# 4. Generate reports
arr-export-enhanced report --service radarr # Creates HTML5 enriched export
arr-export radarr  # Creates CSV export
```

## 📋 Requirements

- **Python 3.8+** (Python 3.11+ recommended for best performance)
- **Radarr v4+** and/or **Sonarr v3+** with API access
- **TRaSH Guides Custom Formats** configured in your applications
- **2GB+ RAM** (4GB+ recommended for large libraries)

## 🚀 Installation

### Recommended Installation

```bash
# Clone the repository
git clone https://github.com/gdadkins/arr-score-exporter.git
cd arr-score-exporter

# Install with all features
pip install -e .
```

### Virtual Environment (Optional)

```bash
# Create isolated environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install
pip install -e .
```

### Development Installation

```bash
# Install with development tools
pip install -e .[dev]

# Run tests
pytest

# Code formatting
black . && isort .
```

## ⚙️ Configuration

### 1. Create Configuration File

```bash
cp config.yaml.example config.yaml
```

### 2. Configure Your Services

```yaml
# Radarr Configuration
radarr:
  url: "http://your-radarr-url:7878"
  api_key: "your_radarr_api_key_here"
  enabled: true

# Sonarr Configuration  
sonarr:
  url: "http://your-sonarr-url:8989"
  api_key: "your_sonarr_api_key_here"
  enabled: true

# Export Settings
export:
  max_workers: 5
  output_dir: "exports"
  generate_dashboard: true
```

### 3. Get Your API Keys

**Radarr/Sonarr**: Settings → General → Security → API Key

### 4. Test Configuration

```bash
arr-export test-config
```

✅ You should see connection confirmations for both services.

## 📋 Usage

### Basic Commands

```bash
# Test configuration and connectivity
arr-export test-config

# Export Radarr with dashboard
arr-export-enhanced report --service radarr

# Export Sonarr with dashboard  
arr-export-enhanced report --service sonarr

# Export both services
arr-export both
```

### Advanced Options

```bash
# Detailed logging
arr-export --verbose radarr

# Custom configuration
arr-export --config custom.yaml radarr

# Custom output directory
arr-export --output-dir /path/to/exports radarr
```

### Example Output

```
🚀 Starting Radarr export...

📋 Configuration:
  ✅ Radarr: http://localhost:7878 (3000 movies)
  💾 Database: ~/.arr-score-exporter/library.db
  ⚙️ Workers: 5 parallel threads

🔄 Processing: ██████████ 100% 3000/3000

📈 Analysis Results:
  🎯 Upgrade candidates: 1,252 files identified
  🔍 Library health: B+ (78.5/100)
  📊 Dashboard: exports/radarr_dashboard_20241129.html
  📄 CSV Export: exports/radarr_export_20241129.csv

✅ Export completed in 45.2 seconds
```

### Legacy Scripts (Optional)

Original monolithic scripts are available in `legacy/` for simple use cases:

```bash
python legacy/export_radarr_scores.py
python legacy/export_sonarr_scores.py
```

## 🌟 Key Features

### 🤖 Intelligent Analysis Engine
- **🎯 Smart Upgrade Detection**: Automatically identifies files that would benefit from quality upgrades
- **📊 Custom Format ROI**: Analyzes which TRaSH Guides formats provide the most value
- **🏆 Quality Profile Scoring**: Compares and rates your quality profile effectiveness
- **🕰️ Trend Monitoring**: Historical tracking shows library improvements over time

### 📊 Interactive Dashboards
- **🎨 Beautiful HTML Reports**: Professional dashboards with responsive design
- **📉 Rich Visualizations**: Charts, graphs, and tables powered by Chart.js
- **🔍 Health at a Glance**: Library health score (A-F grade) with recommendations
- **📎 Export Integration**: Click-to-export data as CSV directly from dashboard

### 📋 Advanced Data Management
- **💾 SQLite Database**: Thread-safe storage with WAL mode for performance
- **📈 Historical Tracking**: Score changes and trends tracked automatically
- **🔄 Export Audit Trail**: Complete log of all export runs with metadata
- **⚙️ Concurrent Processing**: Multi-threaded operations with intelligent rate limiting

### 🚀 Production Ready
- **📝 Rich Terminal UI**: Progress bars, status indicators, and colored output
- **🛡️ Robust Error Handling**: Retry logic, graceful degradation, and detailed logging
- **📦 Multiple Export Formats**: CSV, JSON, HTML, and database storage
- **🔌 Environment Support**: Docker, Kubernetes, and environment variable configuration

## 📄 Output Formats

### 🎨 Interactive HTML Dashboard

![Dashboard Features](https://via.placeholder.com/600x300/34495E/ECF0F1?text=Library+Overview+%7C+Health+Score+%7C+Charts)

**Dashboard Sections:**
- **📈 Library Overview**: Health scores, file counts, score distributions
- **🎯 Upgrade Candidates**: Prioritized list with specific recommendations
- **🔍 Format Analysis**: Custom format effectiveness with ROI metrics
- **🏆 Quality Profiles**: Comparative performance analysis
- **📉 Trend Charts**: Historical improvements and patterns

### 📃 Enhanced CSV Export

```csv
Title,File,Total_Score,Quality_Profile,Codec,Resolution,Size_GB,Custom_Formats
"The Matrix","Movies/The Matrix (1999)/Matrix.2160p.mkv",6150,"4K Remux","x265","2160p",45.2,"Remux Tier 01|HDR10+"
```

**Includes:**
- Complete metadata (codecs, resolutions, file sizes)
- Individual custom format scores and details
- Quality profile mapping and performance data
- Unique identifiers for change tracking

### 💾 Database Storage

**SQLite Database** (`~/.arr-score-exporter/library.db`):
- **Media Files**: Complete file metadata and scoring history
- **Score Trends**: Track improvements and degradations over time
- **Library Statistics**: Aggregate health metrics and benchmarks
- **Export Logs**: Complete audit trail with performance metrics

## 🚀 How It Works

### 🔄 Processing Workflow

```
1. 📋 Configuration → 2. 🔌 API Connection → 3. 📋 Data Collection
                ↓
6. 📄 Export Files ← 5. 🎨 Dashboard Gen ← 4. 🤖 Analysis Engine
```

1. **🔍 Configuration Validation**: Verifies YAML config and tests API connectivity
2. **📋 Parallel Data Collection**: Efficiently fetches all media files and metadata
3. **💾 Database Storage**: Stores data in SQLite with historical change tracking
4. **🤖 Intelligent Analysis**: Identifies upgrade candidates and effectiveness patterns
5. **🎨 Dashboard Generation**: Creates interactive HTML reports with visualizations
6. **📄 Multi-Format Export**: Generates CSV files and database exports

### 🏢 Architecture Highlights

- **🧩 Modular Design**: Clean separation between data, analysis, and presentation layers
- **⚡ High Performance**: Multi-threaded processing with intelligent rate limiting
- **💾 Data Persistence**: SQLite WAL mode for reliable concurrent access
- **🔄 Event Sourcing**: Complete audit trail of all changes and operations
- **🛡️ Error Resilience**: Comprehensive retry logic and graceful degradation

### 🔌 Integration Points

- **TRaSH Guides**: Custom format definitions and scoring methodology
- **Radarr/Sonarr APIs**: Real-time data extraction with proper authentication
- **SQLite Database**: Local storage for historical analysis and caching
- **Modern Web**: Responsive HTML5 dashboards with Chart.js visualizations

## ⚙️ Performance & Tuning

### 🚀 Optimal Configuration

```yaml
export:
  max_workers: 5          # Parallel API calls (adjust based on system)
  retry_attempts: 3       # Automatic retry for failed requests
  retry_delay: 1          # Backoff delay (seconds)
  timeout: 30             # Request timeout
  
dashboard:
  show_upgrade_candidates: 20  # Dashboard display limits
  show_format_analysis: 15     # Format effectiveness entries
```

### 📊 Performance Benchmarks

| Library Size | Processing Time | Memory Usage | Recommended RAM |
|-------------|----------------|--------------|----------------|
| < 1,000 files | < 2 minutes | 100-200MB | 2GB |
| 1,000-5,000 files | 2-10 minutes | 200-400MB | 4GB |
| 5,000+ files | 10+ minutes | 400MB+ | 8GB+ |

### ⚙️ Tuning for Your Environment

**Large Libraries (5,000+ files):**
```yaml
export:
  max_workers: 3          # Reduce load on *Arr services
  retry_attempts: 5       # More retries for reliability
  timeout: 60             # Longer timeout for large requests
```

**Fast Systems:**
```yaml
export:
  max_workers: 8          # Increase parallelism
  retry_delay: 0.5        # Faster retry cycles
```

## 🚑 Troubleshooting

### ✅ Quick Diagnostics

```bash
# Test everything
arr-export test-config

# Detailed logging
arr-export --verbose radarr

# Check database health
sqlite3 ~/.arr-score-exporter/library.db "PRAGMA integrity_check;"
```

### 🚪 Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| **API Connection** | `Connection refused` | Verify URL and API key |
| **Database Lock** | `Database is locked` | ✅ **Fixed in v2.0** |
| **Memory Usage** | `Process killed` | Reduce `max_workers` or increase RAM |
| **Permission Error** | `Cannot write` | Check export directory permissions |

### 🔍 Verification Commands

```bash
# Test Radarr connection
curl "http://your-radarr:7878/api/v3/system/status" -H "X-Api-Key: YOUR_KEY"

# Check database size
ls -lh ~/.arr-score-exporter/library.db

# Verify exports
ls -la exports/
```

**📆 Complete troubleshooting guide: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**

## 📆 Documentation

- **[🏢 Architecture Guide](docs/ARCHITECTURE.md)**: Technical design patterns and system architecture
- **[📚 API Reference](docs/API_REFERENCE.md)**: Complete CLI commands and Python API documentation
- **[🚑 Troubleshooting Guide](docs/TROUBLESHOOTING.md)**: Common issues, solutions, and diagnostics
- **[📋 Usage Guide](USAGE-GUIDE.md)**: Detailed examples and advanced workflows
- **[👨‍💻 Development Docs](docs/development_docs.md)**: Contributing guidelines and development setup

## 🛠️ Development

### 🚀 Quick Setup

```bash
# Clone and setup development environment
git clone https://github.com/gdadkins/arr-score-exporter.git
cd arr-score-exporter

# Install with development tools
pip install -e .[dev]

# Run tests
pytest

# Code quality
black . && isort . && mypy src/
```

### 🧪 Testing

```bash
# Run test suite
pytest tests/ --cov

# Type checking
mypy src/

# Integration tests
arr-export test-config
```

## 🕰️ Recent Updates

### 🎉 v2.0 - Production Ready Release
- ✅ **Enhanced Architecture**: Complete rewrite with modular design
- ✅ **Interactive Dashboards**: Professional HTML reports with Chart.js
- ✅ **Intelligent Analysis**: ML-ready upgrade candidate detection
- ✅ **Database Persistence**: SQLite with WAL mode and historical tracking
- ✅ **Rich Terminal UI**: Modern CLI with progress bars and status indicators
- ✅ **Production Fixes**: Resolved database locking and custom format analysis
- ✅ **Performance Optimized**: Multi-threaded processing with rate limiting

### 🔄 Migration Path
- **Legacy Scripts**: Available in `legacy/` folder for simple use cases
- **Backward Compatibility**: Existing configurations work with enhanced version
- **Gradual Adoption**: Use legacy scripts while transitioning to v2.0 features

## 🤝 Contributing

We welcome contributions! 🎆

```bash
# Quick contribution setup
git fork https://github.com/gdadkins/arr-score-exporter
git clone your-fork-url
cd arr-score-exporter
pip install -e .[dev]

# Make changes, test, and submit PR
```

**See [docs/development_docs.md](docs/development_docs.md) for detailed guidelines.**

## 📄 License

[MIT License](LICENSE) - Free for commercial and personal use

## 🙏 Acknowledgments

- **[🗑️ TRaSH Guides](https://trash-guides.info/)**: Methodology and custom format definitions
- **[🎥 Radarr](https://radarr.video/) & [📺 Sonarr](https://sonarr.tv/) Teams**: Excellent APIs and documentation
- **[🐍 Python Community](https://python.org/)**: Amazing ecosystem of libraries
- **[📈 Chart.js](https://chartjs.org/)**: Beautiful dashboard visualizations

---

<div align="center">

**⭐ Star this repo if it helps optimize your media library! ⭐**

[Report Bug](https://github.com/gdadkins/arr-score-exporter/issues) • [Request Feature](https://github.com/gdadkins/arr-score-exporter/issues) • [View Docs](docs/)

</div>