# Development Documentation

## Architecture Overview

### Design Principles

1. **Single Responsibility**: Each class has one clear purpose
2. **DRY (Don't Repeat Yourself)**: Shared logic is extracted into base classes
3. **Configuration over Code**: Settings are externalized to config files
4. **Fail Fast**: Early validation and clear error messages
5. **Extensibility**: Easy to add new *Arr applications

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Module    │───▶│ ConfigManager   │───▶│   AppConfig     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ RadarrExporter  │───▶│  BaseExporter   │◄───│ SonarrExporter  │
│ SonarrExporter  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                     ┌─────────────────┐
                     │  ArrApiClient   │
                     └─────────────────┘
```

### Class Responsibilities

#### `ConfigManager`
- Load configuration from YAML/JSON files
- Handle environment-specific configs
- Provide reasonable defaults

#### `ArrApiClient`
- HTTP session management with retry logic
- Rate limiting and timeout handling
- Centralized error handling for API calls

#### `BaseExporter`
- Common export workflow (template method pattern)
- Parallel file processing
- Quality profile caching
- CSV output formatting

#### `RadarrExporter` / `SonarrExporter`
- Application-specific API endpoints
- Data structure handling
- Row formatting for CSV output

## Quick Start

### Prerequisites
- Python 3.8+
- Active Radarr/Sonarr instances for testing
- TMDb API key (free from themoviedb.org)

### Development Setup
```bash
# Clone the repository
git clone https://github.com/gdadkins/arr-score-exporter.git
cd arr-score-exporter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Copy and configure settings
cp config.yaml.example config.yaml
# Edit config.yaml with your API keys and URLs

# Run tests
pytest

# Run with coverage
pytest --cov=arr_score_exporter --cov-report=html
```

### Development Commands
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Run linting
flake8 src/ tests/

# Install pre-commit hooks
pre-commit install
```
- [ ] **Web UI**: Simple Flask/FastAPI web interface
- [ ] **Scheduling**: Built-in scheduler for regular exports
- [ ] **Filters**: Export only specific quality profiles or score ranges
- [ ] **Formats**: Support JSON, Excel output formats
- [ ] **Diff Mode**: Compare exports over time
- [ ] **Database Storage**: Store results in SQLite for historical analysis

### Phase 3: Advanced Features
- [ ] **Dashboard**: Real-time monitoring of library quality
- [ ] **Recommendations**: Suggest upgrades based on custom format rules
- [ ] **Integration**: Webhooks for automation systems
- [ ] **Multi-Instance**: Support multiple Radarr/Sonarr instances
- [ ] **Cloud Storage**: Export directly to S3, Google Drive
- [ ] **Notifications**: Slack, Discord, email alerts

### Phase 4: Enterprise Features
- [ ] **REST API**: Full API for integration with other tools
- [ ] **Authentication**: User management and permissions
- [ ] **Plugins**: Extensible plugin system for custom exporters
- [ ] **Clustering**: Distributed processing for large libraries
- [ ] **Analytics**: Advanced reporting and trending

## Code Style Guidelines

### Python Style
- Follow PEP 8
- Use type hints for all public functions
- Maximum line length: 88 characters (Black default)
- Use descriptive variable names
- Prefer composition over inheritance

### Documentation
- All public functions must have docstrings
- Use Google-style docstrings
- Include usage examples in docstrings
- Update README for user-facing changes

### Git Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes with good commit messages
3. Run tests: `pytest`
4. Run quality checks: `pre-commit run --all-files`
5. Push and create pull request

### Testing Guidelines
- Aim for >90% code coverage
- Test both success and failure cases
- Use fixtures for common test data
- Mock external API calls
- Test CLI interface with different arguments

## Common Development Tasks

### Adding a New *Arr Application

1. Create new exporter class inheriting from `BaseExporter`
2. Implement abstract methods:
   - `_fetch_single_file()`
   - `collect_items()`
   - `format_row()`
   - `get_fieldnames()`
3. Add to CLI choices in `main()`
4. Add configuration example
5. Add tests

### Adding New Output Formats

1. Create new output handler in `utils/`
2. Add format option to CLI
3. Update base exporter to support new format
4. Add tests and documentation

### Performance Optimization

1. Profile with `cProfile`: `python -m cProfile script.py`
2. Monitor memory usage with `memory_profiler`
3. Use `asyncio` for I/O bound operations (future enhancement)
4. Consider database caching for large libraries

## Troubleshooting

### Common Issues

#### "API Key Invalid"
- Verify API key in configuration
- Check API key permissions in *Arr settings
- Ensure URL includes protocol (http/https)

#### "Timeout Errors"
- Increase `api_timeout` in configuration
- Reduce `max_workers` to lower concurrent load
- Check network connectivity to *Arr instance

#### "No Data Found"
- Verify *Arr instance has media with files
- Check that custom formats are configured
- Ensure quality profiles are assigned to media

#### "Permission Denied Writing CSV"
- Check file write permissions
- Ensure output directory exists
- Verify disk space availability

### Debugging Tips

1. **Enable verbose logging**: Use `-v` flag
2. **Test API connectivity**: Use browser to access *Arr web interface
3. **Check configuration**: Print loaded config with debug logging
4. **Isolate issues**: Test with small subset using filters
5. **Monitor resources**: Check CPU/memory usage during export

### Performance Tuning

| Library Size | Recommended Settings |
|--------------|---------------------|
| < 1,000 items | `max_workers: 15`, `api_timeout: 30` |
| 1,000 - 5,000 | `max_workers: 20`, `api_timeout: 45` |
| 5,000 - 10,000 | `max_workers: 25`, `api_timeout: 60` |
| > 10,000 items | `max_workers: 30`, `api_timeout: 90`, `request_delay: 0.1` |

### Getting Help

1. Check this documentation first
2. Search existing issues on GitHub
3. Create issue with:
   - Configuration (redact API keys)
   - Full error message
   - Steps to reproduce
   - Environment details (OS, Python version, *Arr version)
