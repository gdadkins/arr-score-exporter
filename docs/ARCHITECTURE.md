# Architecture Overview

Technical design and implementation patterns for the *Arr Custom Format Score Exporter.

## Design Principles

- **Single Responsibility**: Each class has one clear purpose
- **Template Method Pattern**: Common workflows with service-specific implementations
- **Fail Fast**: Early validation with detailed error messages
- **Graceful Degradation**: Continue processing despite individual failures

## Component Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ CLI Interface   │───▶│ Config Manager  │───▶│ YAML + ENV Vars │
│ (Click-based)   │    │ (Validation)    │    │ (Multi-source)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ RadarrExporter  │───▶│  BaseExporter   │◄───│ SonarrExporter  │
│ (Service-spec)  │    │ (Template)      │    │ (Service-spec)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                     ┌─────────────────┐
                     │  ArrApiClient   │
                     │ (HTTP + Retry)  │
                     └─────────────────┘
                                 │
                                 ▼
      ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
      │ DatabaseManager │    │ Analysis Engine │    │ HTML Reporter   │
      │ (SQLite + WAL)  │    │ (Intelligence)  │    │ (Charts + Dash) │
      └─────────────────┘    └─────────────────┘    └─────────────────┘
               │                       │                       │
               ▼                       ▼                       ▼
      ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
      │ Historical Data │    │ Smart Analysis  │    │ Interactive UI  │
      │ Score Tracking  │    │ Upgrade Detection│    │ Chart.js + CSS │
      └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Components

### Configuration (`config.py`)
- YAML configuration with environment variable overrides
- Validation and error reporting
- Multi-source configuration discovery

```python
config = Config()  # Auto-discovery
config = Config('/path/to/config.yaml')  # Specific file
```

### API Client (`api_client.py`)
- HTTP communication with retry logic
- Rate limiting and circuit breaker patterns
- Comprehensive error handling

```python
client = ArrApiClient(url, api_key)
movies = client.get('/movie')
```

### Base Exporter (`exporters/base.py`)
- Template method pattern for export workflows
- Common database operations
- Progress tracking and error handling

```python
class BaseExporter:
    def export():
        self._validate_config()
        items = self._get_all_items()     # Implemented by subclass
        self._process_items(items)        # Common logic
        return self._generate_output()    # Common logic
```

### Service Exporters
- **RadarrExporter**: Movie-specific processing
- **SonarrExporter**: Series/episode processing
- Both extend BaseExporter with service-specific logic

### Database (`models/database.py`)
- SQLite with WAL mode for concurrency
- Thread-safe operations
- Historical tracking and analytics

```python
db = DatabaseManager()
db.store_media_file(media_file)
stats = db.calculate_library_stats("radarr")
```

### Analysis Engine (`analysis/analyzer.py`)
- Intelligent upgrade candidate identification with priority scoring
- Custom format effectiveness analysis and impact ratings
- Library health scoring with A-F grading system
- Historical trend analysis with velocity metrics
- Smart file categorization (premium, upgrade-worthy, problematic)
- Quality profile performance analysis

```python
analyzer = IntelligentAnalyzer(db)
candidates = analyzer.identify_upgrade_candidates("radarr")
health = analyzer.generate_library_health_report("radarr")
categories = analyzer.categorize_files_intelligently("radarr")
trends = analyzer.analyze_historical_trends("radarr")
```

### HTML Reporter (`reporting/html_reporter.py`)
- Interactive HTML reports with Chart.js visualizations
- Responsive design with mobile support
- Export functionality and filtering built-in
- Enhanced visualizations: scatter plots, heatmaps, impact matrices

```python
reporter = HTMLReporter()
html_path = reporter.generate_library_health_report(
    health_report=health_report,
    library_stats=library_stats
)
```

## Data Flow

### Basic CSV Export
1. **Configuration** → Load and validate YAML + environment variables
2. **API Connection** → Test connectivity and gather service info
3. **Data Collection** → Fetch movies/series with parallel workers
4. **CSV Generation** → Format and write CSV files
5. **Cleanup** → Close connections and report results

### Enhanced Dashboard Export
1. **Configuration** → Same as basic export
2. **Database Setup** → Initialize SQLite with WAL mode for concurrency
3. **Data Collection** → Fetch and store in database with historical tracking
4. **Intelligent Analysis** → Run upgrade detection, format analysis, trend analysis
5. **Dashboard Generation** → Create interactive HTML with Chart.js visualizations
6. **Export** → Generate both CSV and comprehensive HTML dashboard
7. **Historical Tracking** → Store score changes and library evolution data

## Concurrency Model

### Thread Pool Execution
- Configurable worker count (default: 5)
- I/O-bound operations (API calls, database writes)
- Graceful handling of failures

### Rate Limiting
- Adaptive rate limiting based on API response
- Circuit breaker for failing endpoints
- Exponential backoff with jitter

### Database Concurrency
- WAL mode for concurrent read/write access
- Connection pooling with proper cleanup
- Transaction management for data integrity

## Error Handling Strategy

### Fail Fast
- Configuration validation at startup
- API connectivity testing before processing
- Early error detection and reporting

### Graceful Degradation
- Continue processing despite individual item failures
- Retry logic for transient network issues
- Comprehensive logging for debugging

### Error Classification
- **Configuration Errors**: User fixable (API keys, URLs)
- **Network Errors**: Retry with backoff
- **Data Errors**: Log and continue processing
- **System Errors**: Fail fast with clear messages

## Extensibility Points

### Adding New Services
1. Extend `BaseExporter` class
2. Implement service-specific methods
3. Add CLI commands and configuration
4. Update database schema if needed

### Adding Analysis Features
1. Extend `IntelligentAnalyzer` class
2. Create new analysis methods
3. Add dashboard visualizations
4. Update configuration options

### Adding Export Formats
1. Create new exporter strategy
2. Register with export factory
3. Add CLI options
4. Implement format-specific validation

## Performance Considerations

### Memory Management
- Streaming processing for large datasets
- Configurable batch sizes
- Memory monitoring and cleanup

### Database Optimization
- Proper indexing for query performance
- WAL mode for concurrent access
- Regular VACUUM operations for maintenance

### Network Efficiency
- Connection pooling and reuse
- Request pipelining where possible
- Compression for large responses

## Testing Strategy

### Unit Tests
- Individual component testing
- Mock API responses
- Database operations with in-memory SQLite

### Integration Tests
- End-to-end workflows
- Real API testing (with rate limiting)
- Performance testing with large datasets

### Analysis Tests
- Algorithm correctness validation
- Statistical calculation verification
- Edge case handling

## Security Considerations

### Credential Management
- API keys never logged or displayed
- Environment variable support
- Secure configuration file handling

### Network Security
- HTTPS enforcement for external communications
- Request validation and sanitization
- Rate limiting protection

### Data Security
- Local SQLite database only
- No sensitive data transmission
- Secure file permissions

## Future Enhancements

### Planned Features
- Machine learning integration for predictive analysis
- Real-time monitoring and alerting
- Multi-tenant support for enterprise use
- API gateway for external integrations

### Performance Improvements
- Async/await architecture migration
- Distributed processing for large libraries
- Redis caching layer integration
- Database sharding for massive datasets

## Current State (v2.0)

### Implemented ✅
- **Enhanced Database Architecture**: SQLite WAL mode with historical score tracking
- **Intelligent Analysis Engine**: AI-powered upgrade recommendations with priority scoring
- **Interactive HTML Dashboards**: Chart.js visualizations with responsive design
- **Advanced Analytics**: Score distribution, format effectiveness, quality profile analysis
- **Smart Categorization**: Automatic file classification into 10 intelligent categories
- **Historical Trend Analysis**: Velocity metrics and pattern detection
- **Enhanced Visualizations**: Scatter plots, heatmaps, impact matrices
- **Dashboard Interactivity**: Filtering, sorting, export functionality
- **Modern CLI**: Rich terminal output with progress indicators
- **Robust Error Handling**: Comprehensive retry mechanisms and graceful degradation

### Recently Fixed ✅
- Database locking issues resolved with WAL mode implementation
- Custom format analysis correlation improved with intelligent algorithms
- Thread safety implemented throughout the codebase
- Memory optimization for large libraries (5000+ files)
- Enhanced dashboard performance with optimized chart rendering

### Dashboard Features ✅
- **Library Health Score**: A-F grading system with detailed breakdown
- **Upgrade Candidates**: Priority-ranked recommendations with potential score gains
- **Format Effectiveness**: Impact analysis of custom formats with usage statistics
- **Quality Profile Analysis**: Performance comparison across different profiles
- **Historical Trends**: Time-series analysis with improvement/degradation velocity
- **Interactive Charts**: Score distribution, profile performance, format impact matrices
- **Smart Filters**: Dynamic filtering by score range, profiles, priority levels
- **Export Functionality**: CSV export with filtered data preservation

The architecture has evolved from simple CSV export scripts to a comprehensive library analysis platform with advanced intelligence while maintaining backward compatibility and clean separation of concerns.