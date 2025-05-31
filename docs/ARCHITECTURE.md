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
      │ DatabaseManager │    │ Analysis Engine │    │ Dashboard Gen   │
      │ (SQLite + WAL)  │    │ (Intelligence)  │    │ (HTML + Charts) │
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
- Upgrade candidate identification
- Custom format effectiveness analysis
- Library health scoring

```python
analyzer = IntelligentAnalyzer(db)
candidates = analyzer.identify_upgrade_candidates("radarr")
health = analyzer.generate_library_health_report("radarr")
```

### Dashboard Generator (`reporting/dashboard.py`)
- Interactive HTML reports with Chart.js
- Responsive design with mobile support
- Export functionality built-in

```python
generator = DashboardGenerator()
html_path = generator.generate_dashboard(
    service_type="radarr",
    media_files=files,
    analysis_results=analysis
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
2. **Database Setup** → Initialize SQLite with WAL mode
3. **Data Collection** → Fetch and store in database with historical tracking
4. **Analysis** → Run intelligent analysis algorithms
5. **Dashboard** → Generate interactive HTML with charts
6. **Export** → Create both CSV and HTML outputs

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
- Enhanced database architecture with SQLite WAL mode
- Intelligent analysis engine with upgrade recommendations
- Interactive HTML dashboards with Chart.js
- Historical tracking and trend analysis
- Modern CLI with rich terminal output
- Robust error handling and retry mechanisms

### Recently Fixed ✅
- Database locking issues resolved
- Custom format analysis correlation improved
- Thread safety implemented throughout
- Memory optimization for large libraries

The architecture has evolved from simple CSV export scripts to a comprehensive library analysis platform while maintaining backward compatibility and clean separation of concerns.