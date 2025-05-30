# Enhanced Architecture Documentation

## Overview

The Arr Score Exporter has evolved into a comprehensive library analysis and optimization platform. The enhanced architecture combines the original score extraction capabilities with intelligent analysis, historical tracking, and interactive reporting. The system is built using modern Python practices with a focus on maintainability, extensibility, and data-driven insights.

## Enhanced Design Principles

### 1. Single Responsibility Principle (SRP)
Each class has one clear purpose:
- `Config`: Advanced configuration management with validation
- `ArrApiClient`: HTTP communication with retry logic and rate limiting
- `DatabaseManager`: SQLite persistence with thread safety
- `BaseExporter`: Template method pattern for export workflows
- `RadarrExporter`/`SonarrExporter`: Service-specific implementations with analysis
- `IntelligentAnalyzer`: Advanced analytics and insights generation
- `DashboardGenerator`: Interactive HTML report generation
- `CSVWriter`: Enhanced CSV output with rich formatting

### 2. Open/Closed Principle (OCP)
The system is open for extension but closed for modification:
- New Arr services can be added by extending `BaseExporter`
- New analysis algorithms can be added to `IntelligentAnalyzer`
- New dashboard components can be plugged into `DashboardGenerator`
- New export formats can be added via strategy pattern
- Configuration options are externalized and validated

### 3. Don't Repeat Yourself (DRY)
Shared functionality is extracted into base classes and utilities:
- Common API patterns with retry logic in `ArrApiClient`
- Export workflow template with database integration in `BaseExporter`
- Thread-safe database operations in `DatabaseManager`
- Rich data models with comprehensive metadata
- Common analysis patterns in `IntelligentAnalyzer`
- Reusable dashboard components in reporting module

## Enhanced Architecture Patterns

### Template Method Pattern
`BaseExporter` implements the template method pattern where the overall algorithm is defined in the base class, but specific steps are implemented by subclasses:

```python
def export_with_analysis(self):
    # 1. Initialize and validate
    self._initialize_export()
    
    # 2. Get all items (implemented by subclass)
    items = self._get_all_items()
    
    # 3. Process items with database storage (common logic)
    for item in items:
        media_file = self._process_item(item)     # subclass specific
        self.db.store_media_file(media_file)      # common persistence
    
    # 4. Generate analysis and dashboard (common workflow)
    analysis_results = self._generate_analysis()
    dashboard_path = self._generate_dashboard(analysis_results)
    
    return self._compile_results(analysis_results, dashboard_path)
```

### Strategy Pattern
Multiple pluggable strategies are implemented:
- **Export Strategies**: CSV, JSON, database storage
- **Analysis Strategies**: Upgrade candidate identification, format effectiveness, quality profile analysis
- **Dashboard Strategies**: Different chart types, themes, and layouts
- **Connection Strategies**: Thread-safe database connections with WAL mode, retry logic

### Factory Pattern
Multiple factories enable extensibility:
- **Exporter Factory**: Creates service-specific exporters (Radarr/Sonarr)
- **Analyzer Factory**: Creates analysis engines based on service type
- **Dashboard Factory**: Creates dashboard generators with different configurations
- **Connection Factory**: Creates optimized database connections

## Enhanced Component Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Enhanced CLI    │───▶│ Config Manager  │───▶│ YAML + ENV Vars │
│ (Rich Output)   │    │ (Validation)    │    │ (Multi-source)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ RadarrExporter  │───▶│  BaseExporter   │◄───│ SonarrExporter  │
│ (Enhanced)      │    │ (DB Integration)│    │ (Enhanced)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                     ┌─────────────────┐
                     │  ArrApiClient   │
                     │ (Retry + Rate   │
                     │   Limiting)     │
                     └─────────────────┘
                                 │
                                 ▼
      ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
      │ DatabaseManager │    │ Intelligent     │    │ Dashboard       │
      │ (Thread-Safe    │    │ Analyzer        │    │ Generator       │
      │  SQLite + WAL)  │    │ (ML-Ready)      │    │ (Interactive)   │
      └─────────────────┘    └─────────────────┘    └─────────────────┘
                │                       │                       │
                ▼                       ▼                       ▼
      ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
      │ Rich Data       │    │ Analysis        │    │ HTML Reports    │
      │ Models          │    │ Results         │    │ (Charts & CSS)  │
      │ (Historical)    │    │ (Insights)      │    │                 │
      └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Enhanced Key Components

### Configuration Management (`config.py`)
- **Advanced YAML Configuration**: Multi-source configuration with inheritance
- **Environment Variable Override**: Complete environment variable support
- **Validation Engine**: Comprehensive validation with detailed error messages
- **Auto-Discovery**: Searches multiple locations for configuration files
- **Dynamic Settings**: Runtime configuration updates and validation

### Enhanced API Clients (`api_client.py`)
- **ArrApiClient**: Robust Radarr/Sonarr API communication
  - **Smart Retry Logic**: Exponential backoff with jitter
  - **Rate Limiting**: Configurable request throttling
  - **Connection Pooling**: Efficient HTTP session management
  - **Comprehensive Logging**: Detailed request/response logging
  - **Error Classification**: Intelligent error handling by type
  - **Health Monitoring**: API endpoint health checks

### Enhanced Base Exporter (`exporters/base.py`)
- **Template Method Evolution**: Database-integrated workflow template
- **Thread-Safe Processing**: Concurrent processing with proper synchronization
- **Progress Tracking**: Real-time progress reporting with rich terminal output
- **Comprehensive Caching**: Quality profiles, custom formats, and metadata caching
- **Error Recovery**: Graceful degradation and automatic retry mechanisms
- **Performance Metrics**: Detailed timing and throughput analysis

### Enhanced Service-Specific Exporters
- **RadarrExporter** (`exporters/radarr.py`): 
  - Movie-specific analysis with genre and year-based insights
  - 4K/HDR format optimization recommendations
  - Collection-based analysis and recommendations
  - Integration with TMDb for enhanced metadata
  
- **SonarrExporter** (`exporters/sonarr.py`):
  - Episode-level analysis with series-wide insights
  - Season-based quality consistency analysis
  - Series completion tracking and recommendations
  - Multi-season upgrade candidate prioritization

### Enhanced Utilities and New Components

#### Database Layer (`models/database.py`)
- **Thread-Safe SQLite**: WAL mode with proper locking mechanisms
- **Rich Data Models**: Comprehensive metadata tracking
- **Historical Tracking**: Score changes and trend analysis over time
- **Performance Optimization**: Indexes and query optimization
- **Migration Support**: Database schema versioning

#### Analysis Engine (`analysis/analyzer.py`)
- **Intelligent Upgrade Candidate Identification**: Multi-factor analysis
- **Custom Format Effectiveness Analysis**: ROI-based format evaluation
- **Quality Profile Optimization**: Performance-based recommendations
- **Library Health Monitoring**: Comprehensive health scoring
- **Trend Analysis**: Historical data analysis and predictions

#### Dashboard Generation (`reporting/dashboard.py`)
- **Interactive HTML Reports**: Rich, responsive dashboards
- **Chart Generation**: Multiple chart types with Chart.js integration
- **Responsive Design**: Mobile-friendly layouts
- **Export Functionality**: Dashboard-to-CSV export capabilities
- **Theming Support**: Light/dark themes with customization

#### Enhanced CSV Writer (`utils/csv_writer.py`)
- **Rich Metadata Export**: Comprehensive file information
- **Multiple Export Formats**: Standard and detailed CSV formats
- **Analysis-Specific Exports**: Specialized exports for different analysis types
- **Unicode Support**: Proper handling of international characters

## Enhanced Error Handling Strategy

### 1. Fail Fast with Context
- **Configuration Validation**: Immediate failure with detailed validation messages
- **Dependency Checking**: Pre-flight checks for all required dependencies
- **API Connectivity**: Early connection testing with detailed diagnostics

### 2. Intelligent Graceful Degradation
- **Network Resilience**: Multi-layer retry with circuit breaker pattern
- **Database Resilience**: Connection pooling with automatic failover
- **Partial Processing**: Continue processing despite individual item failures
- **API Rate Limiting**: Dynamic backoff with quota monitoring

### 3. Structured Logging and Monitoring
- **Rich Terminal Output**: Progress bars, status indicators, and color coding
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Performance Monitoring**: Real-time metrics and performance tracking
- **Error Classification**: Categorized error reporting with severity levels
- **Health Dashboards**: System health monitoring and alerting

### 4. Recovery Mechanisms
- **Database Recovery**: Automatic schema migration and corruption recovery
- **Export Recovery**: Resume interrupted exports from last checkpoint
- **Analysis Recovery**: Cached intermediate results for large datasets

## Enhanced Concurrency Model

### Advanced Parallel Processing
- **ThreadPoolExecutor**: Optimized for I/O-bound API operations
- **Dynamic Worker Scaling**: Adaptive worker count based on system performance
- **Task Prioritization**: Critical tasks processed first
- **Memory Management**: Bounded queues to prevent memory exhaustion
- **Progress Coordination**: Thread-safe progress tracking and reporting

### Intelligent Rate Limiting
- **Adaptive Rate Limiting**: Dynamic adjustment based on API response times
- **Circuit Breaker Pattern**: Automatic circuit breaking for failing APIs
- **Quota Management**: Intelligent quota usage and conservation
- **Priority Queuing**: High-priority requests bypass rate limits when possible

### Database Concurrency
- **WAL Mode**: Write-Ahead Logging for better concurrent access
- **Connection Pooling**: Efficient connection reuse and management
- **Transaction Management**: ACID compliance with proper isolation
- **Deadlock Prevention**: Sophisticated locking strategies
- **Read/Write Optimization**: Separate optimizations for read-heavy vs write-heavy operations

## Enhanced Extensibility Points

### Adding New Arr Services
1. **Extend BaseExporter**: Implement service-specific methods
2. **Database Schema**: Add service-specific fields to data models
3. **Analysis Integration**: Implement service-specific analysis algorithms
4. **Dashboard Components**: Create service-specific dashboard sections
5. **CLI Integration**: Add commands and validation for new service

### Adding New Analysis Algorithms
1. **Extend IntelligentAnalyzer**: Add new analysis methods
2. **Data Models**: Create analysis-specific data classes
3. **Dashboard Integration**: Add visualization components
4. **Configuration Options**: Add analysis-specific settings
5. **Performance Optimization**: Implement caching and indexing

### Adding New Export Formats
1. **Strategy Implementation**: Create new export strategy classes
2. **Format Registration**: Register format with export factory
3. **CLI Options**: Add command-line options for new format
4. **Validation**: Implement format-specific validation
5. **Testing**: Comprehensive test coverage for new format

### Adding New Dashboard Components
1. **Chart Types**: Implement new Chart.js chart types
2. **Data Processing**: Create data transformation pipelines
3. **Responsive Design**: Ensure mobile compatibility
4. **Theming**: Support for light/dark themes
5. **Interactivity**: Add filtering and drill-down capabilities

## Comprehensive Testing Strategy

### Unit Tests
- **Database Operations**: SQLite operations with in-memory databases
- **Analysis Algorithms**: Mathematical correctness of analysis functions
- **Configuration Validation**: All configuration scenarios and edge cases
- **Data Models**: Serialization/deserialization and validation
- **Mock API Integration**: Comprehensive API response mocking

### Integration Tests
- **End-to-End Workflows**: Complete export and analysis pipelines
- **Database Integration**: Real SQLite operations with test databases
- **Performance Testing**: Large dataset processing and memory usage
- **API Integration**: Real API testing with rate limiting
- **Cross-Platform Testing**: Windows, Linux, and macOS compatibility

### Analysis Tests
- **Algorithm Validation**: Mathematical correctness of analysis algorithms
- **Statistical Tests**: Validate statistical calculations and insights
- **Edge Case Handling**: Empty datasets, extreme values, corrupted data
- **Performance Benchmarks**: Analysis performance with various dataset sizes

### Dashboard Tests
- **Rendering Tests**: HTML/CSS validation and visual regression testing
- **Data Accuracy**: Chart data accuracy and formatting
- **Responsive Design**: Multi-device and screen size testing
- **Accessibility**: WCAG compliance and screen reader compatibility

### Database Tests
- **Concurrency Testing**: Multi-threaded access patterns
- **Migration Testing**: Schema upgrade and downgrade scenarios
- **Corruption Recovery**: Database integrity and recovery testing
- **Performance Testing**: Query optimization and indexing effectiveness

## Enhanced Performance Considerations

### Memory Optimization
- **Streaming Architecture**: Process large datasets without loading everything into memory
- **Intelligent Caching**: Multi-level caching with LRU eviction
- **Memory Monitoring**: Real-time memory usage tracking and alerts
- **Garbage Collection**: Optimized object lifecycle management
- **Batch Processing**: Configurable batch sizes for optimal memory usage

### Database Performance
- **Query Optimization**: Sophisticated indexing strategies
- **Connection Pooling**: Efficient connection reuse and management
- **WAL Mode**: Write-Ahead Logging for better concurrent performance
- **Vacuum Operations**: Automated database maintenance
- **Prepared Statements**: Pre-compiled queries for better performance

### Network Efficiency
- **Connection Reuse**: HTTP/2 and connection pooling
- **Request Pipelining**: Parallel request processing where possible
- **Compression**: Automatic gzip compression for API responses
- **CDN Integration**: Static asset optimization for dashboard components
- **Bandwidth Monitoring**: Network usage tracking and optimization

### Processing Performance
- **CPU Optimization**: Multi-core processing with optimal thread allocation
- **I/O Optimization**: Asynchronous I/O operations where beneficial
- **Algorithm Optimization**: Efficient algorithms for analysis operations
- **Profiling Integration**: Built-in performance profiling and monitoring
- **Scalability Testing**: Performance testing across various system configurations

## Enhanced Security Considerations

### Credential Management
- **API Key Protection**: Never logged, displayed, or stored in plain text
- **Environment Variable Security**: Secure loading with validation
- **Configuration Encryption**: Support for encrypted configuration files
- **Credential Rotation**: Support for API key rotation without downtime
- **Audit Logging**: Comprehensive access logging without credential exposure

### Network Security
- **TLS Enforcement**: HTTPS/TLS 1.2+ enforcement for all external communications
- **Certificate Validation**: Strict certificate validation and pinning
- **Request Sanitization**: Input validation and sanitization for all API requests
- **Rate Limiting**: Protection against abuse and DoS attacks
- **Firewall Integration**: Support for enterprise firewall configurations

### Data Security
- **Database Encryption**: At-rest encryption for sensitive database content
- **PII Protection**: Careful handling of personally identifiable information
- **Access Control**: Role-based access control for multi-user environments
- **Data Retention**: Configurable data retention and purging policies
- **Export Security**: Secure export file handling and permissions

### Application Security
- **Input Validation**: Comprehensive validation of all user inputs
- **SQL Injection Prevention**: Parameterized queries and prepared statements
- **XSS Prevention**: Output encoding for dashboard HTML generation
- **Dependency Security**: Regular security updates and vulnerability scanning
- **Error Handling**: Secure error handling without information disclosure

## Future Enhancements

### Phase 3 Features
- **Machine Learning Integration**: 
  - Predictive upgrade recommendations
  - Anomaly detection for quality degradation
  - Smart format optimization based on viewing patterns
  - Automated quality profile tuning

- **Advanced Analytics**:
  - Cost-benefit analysis for storage optimization
  - Viewing pattern analysis integration
  - Quality vs storage efficiency optimization
  - Trend prediction and forecasting

### Performance Optimizations
- **Async/Await Architecture**: Complete migration to async for better scalability
- **Distributed Processing**: Multi-node processing for large libraries
- **Caching Layer**: Redis integration for distributed caching
- **Database Sharding**: Horizontal scaling for massive datasets
- **CDN Integration**: Global content delivery for dashboard assets

### Integration Expansion
- **Media Server Integration**:
  - Jellyfin complete integration
  - Emby advanced features
  - Plex integration for comparison analysis
  - Kodi library management

- **Notification Systems**:
  - Slack/Discord integration
  - Email reporting and alerts
  - Webhook support for custom integrations
  - Mobile app notifications

- **Third-Party Services**:
  - Trakt.tv viewing data integration
  - IMDb Pro features
  - Rotten Tomatoes integration
  - Streaming service availability tracking

### Enterprise Features
- **Multi-Tenant Support**: Support for multiple libraries and users
- **Role-Based Access Control**: Granular permissions and access control
- **API Gateway**: RESTful API for external integrations
- **Enterprise SSO**: LDAP/SAML authentication integration
- **Compliance Features**: GDPR, CCPA compliance tools

### Advanced Dashboard Features
- **Real-Time Updates**: WebSocket integration for live updates
- **Custom Dashboards**: User-configurable dashboard layouts
- **Export Scheduling**: Automated report generation and distribution
- **Collaborative Features**: Shared dashboards and annotations
- **Mobile App**: Native mobile application for iOS/Android

## Current State (v2.0)

### Implemented Features ✅
- **Enhanced Database Architecture**: SQLite with WAL mode and thread safety
- **Intelligent Analysis Engine**: Upgrade candidates, format effectiveness, quality profiles
- **Interactive Dashboards**: Rich HTML reports with responsive design
- **Historical Tracking**: Score changes and trend analysis over time
- **Modern CLI**: Rich terminal output with progress bars and status indicators
- **Configuration Management**: Advanced YAML configuration with validation
- **Error Recovery**: Robust error handling with automatic retry mechanisms
- **Performance Optimization**: Concurrent processing with proper resource management

### Recently Fixed Issues ✅
- **Database Locking**: Resolved SQLite concurrency issues with improved connection management
- **Custom Format Analysis**: Fixed correlation logic for meaningful effectiveness insights
- **Thread Safety**: Implemented proper locking mechanisms for concurrent operations
- **Memory Management**: Optimized memory usage for large library processing

### Architecture Maturity
The current architecture represents a significant evolution from the original simple CSV export scripts to a comprehensive library analysis platform. The system now provides:

1. **Data Persistence**: Complete historical tracking with SQLite database
2. **Intelligent Insights**: Advanced analysis algorithms for optimization recommendations
3. **Professional Reporting**: Interactive dashboards with export capabilities
4. **Production Ready**: Robust error handling, logging, and monitoring
5. **Extensible Design**: Clean architecture for future enhancements

The enhanced architecture maintains backward compatibility with legacy scripts while providing a modern, scalable foundation for future development.