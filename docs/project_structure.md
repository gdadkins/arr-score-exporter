# Enhanced Project Structure

## Current Architecture (v2.0)

```
arr-score-exporter/
├── README.md                           # Enhanced overview with features
├── LICENSE                             # MIT License
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Modern Python packaging config
├── config.yaml.example                # Configuration template
├── arr_score_exporter.py              # Main CLI script (legacy compatible)
├── run_enhanced.py                     # Windows-friendly launcher
├── CLAUDE.md                           # Claude Code development instructions
├── TODO.md                             # Development roadmap
├── USAGE-GUIDE.md                      # Detailed usage documentation
│
├── src/                                # Enhanced modular source code
│   └── arr_score_exporter/
│       ├── __init__.py                 # Package initialization
│       ├── cli.py                      # Legacy CLI interface
│       ├── enhanced_cli.py             # Modern Rich CLI with progress bars
│       ├── config.py                   # Advanced YAML configuration management
│       ├── api_client.py               # HTTP clients with retry logic
│       │
│       ├── exporters/                  # Export implementations
│       │   ├── __init__.py
│       │   ├── base.py                 # Template method base exporter
│       │   ├── radarr.py               # Radarr-specific implementation
│       │   └── sonarr.py               # Sonarr-specific implementation
│       │
│       ├── models/                     # Enhanced data models
│       │   ├── __init__.py
│       │   └── database.py             # SQLite models with thread safety
│       │
│       ├── analysis/                   # Intelligent analysis engine
│       │   ├── __init__.py
│       │   └── analyzer.py             # Advanced analytics & insights
│       │
│       ├── reporting/                  # Dashboard and report generation
│       │   ├── __init__.py
│       │   └── dashboard.py            # Interactive HTML dashboard generator
│       │
│       └── utils/                      # Utility modules
│           ├── __init__.py
│           └── csv_writer.py           # Enhanced CSV output utilities
│
├── legacy/                             # Original monolithic scripts
│   ├── export_radarr_scores.py        # Original Radarr script
│   └── export_sonarr_scores.py        # Original Sonarr script
│
├── tests/                              # Comprehensive test suite
│   ├── __init__.py
│   ├── test_config.py                  # Configuration testing
│   ├── test_database.py               # Database operations testing
│   ├── test_exporters.py              # Export workflow testing
│   ├── test_analysis.py               # Analysis engine testing
│   ├── test_dashboard.py              # Dashboard generation testing
│   └── fixtures/
│       ├── sample_radarr_response.json
│       ├── sample_sonarr_response.json
│       └── test_config.yaml
│
├── docs/                               # Comprehensive documentation
│   ├── ARCHITECTURE.md                 # Enhanced system design & patterns
│   ├── API_REFERENCE.md                # Complete CLI and Python API docs
│   ├── TROUBLESHOOTING.md              # Enhanced troubleshooting guide
│   ├── development_docs.md             # Development setup & contributing
│   └── project_structure.md            # This file
│
├── examples/                           # Usage examples and templates
│   ├── config_examples.md              # Configuration examples
│   ├── example_radarr.csv              # Sample Radarr export
│   └── example_sonarr.csv              # Sample Sonarr export
│
├── scripts/                            # Development and utility scripts
│   ├── test_quick.py                   # Quick system validation
│   ├── test_analysis.py                # Analysis functionality testing
│   ├── check_scores.py                 # Database score analysis
│   └── check_formats.py               # Custom format data analysis
│
└── exports/                            # Generated output directory
    ├── radarr_export_YYYYMMDD_HHMMSS.csv
    ├── radarr_dashboard_YYYYMMDD_HHMMSS.html
    ├── sonarr_export_YYYYMMDD_HHMMSS.csv
    └── sonarr_dashboard_YYYYMMDD_HHMMSS.html
```

## Enhanced Architecture Components

### Core Application Structure

#### Entry Points
- **`arr_score_exporter.py`**: Main CLI script with legacy compatibility
- **`run_enhanced.py`**: Windows-friendly launcher with enhanced output
- **`src/arr_score_exporter/enhanced_cli.py`**: Modern CLI with Rich formatting

#### Configuration Management
- **`config.py`**: Advanced YAML configuration with validation
- **`config.yaml.example`**: Template with all available options
- **Environment variable support**: Complete override capability

#### Data Layer
- **`models/database.py`**: 
  - Thread-safe SQLite operations with WAL mode
  - Rich data models with comprehensive metadata
  - Historical tracking and trend analysis
  - Export run logging and audit trail

#### Business Logic
- **`exporters/base.py`**: Template method pattern for export workflows
- **`exporters/radarr.py`**: Movie-specific implementation with analysis
- **`exporters/sonarr.py`**: Series/episode-specific implementation
- **`analysis/analyzer.py`**: Intelligent analysis engine

#### Presentation Layer
- **`reporting/dashboard.py`**: Interactive HTML dashboard generation
- **`utils/csv_writer.py`**: Enhanced CSV export utilities
- **Rich terminal output**: Progress bars and status indicators

### Enhanced Features Architecture

#### Database Architecture
```
SQLite Database (~/.arr-score-exporter/library.db)
├── media_files                 # Complete file metadata
│   ├── Comprehensive file information
│   ├── Custom format details (JSON)
│   ├── Quality profile mapping
│   └── Service-specific fields
│
├── score_history              # Historical score tracking
│   ├── Score change events
│   ├── Change type classification
│   └── Temporal analysis data
│
├── library_stats              # Aggregate statistics
│   ├── Library-wide metrics
│   ├── Quality profile analysis
│   └── Format effectiveness data
│
└── export_runs               # Audit trail
    ├── Export execution logs
    ├── Performance metrics
    └── Error tracking
```

#### Analysis Engine Architecture
```
IntelligentAnalyzer
├── Upgrade Candidate Identification
│   ├── Multi-factor scoring analysis
│   ├── Priority ranking (1=critical, 4=low)
│   ├── Potential score gain calculation
│   └── Specific recommendations
│
├── Custom Format Effectiveness
│   ├── Format usage correlation analysis
│   ├── Score contribution analysis
│   ├── Impact rating (high/medium/low/negative)
│   └── Optimization recommendations
│
├── Quality Profile Analysis
│   ├── Profile performance comparison
│   ├── Score distribution analysis
│   ├── Effectiveness rating
│   └── Configuration recommendations
│
└── Library Health Monitoring
    ├── Overall health scoring (0-100)
    ├── Health grade assignment (A-F)
    ├── Trend analysis and prediction
    └── Actionable insights generation
```

#### Dashboard Architecture
```
Interactive HTML Dashboard
├── Overview Section
│   ├── Key metrics and health scores
│   ├── File count and distribution
│   └── Export summary information
│
├── Analysis Sections
│   ├── Upgrade candidates with priorities
│   ├── Custom format effectiveness charts
│   ├── Quality profile comparisons
│   └── Score trend visualizations
│
├── Interactive Features
│   ├── Responsive design for mobile/desktop
│   ├── Chart.js integration for visualizations
│   ├── Filterable and sortable tables
│   └── Export functionality to CSV
│
└── Styling and Themes
    ├── Light/dark theme support
    ├── Professional styling with CSS
    ├── Print-friendly layouts
    └── Accessibility compliance
```

## Key Architectural Improvements

### 1. Separation of Concerns
- **Configuration**: Centralized YAML-based configuration management
- **Data Access**: Clean database layer with proper abstraction
- **Business Logic**: Service-specific exporters with common base
- **Analysis**: Dedicated intelligent analysis engine
- **Presentation**: Separate dashboard and CSV output modules

### 2. Design Patterns Implementation
- **Template Method**: `BaseExporter` defines workflow, subclasses implement specifics
- **Strategy Pattern**: Pluggable export formats and analysis algorithms
- **Factory Pattern**: Service-specific exporter creation
- **Observer Pattern**: Progress tracking and status updates

### 3. Modern Python Practices
- **Type Annotations**: Complete type coverage throughout codebase
- **Data Classes**: Rich data models with validation
- **Context Managers**: Proper resource management for database connections
- **Async Support**: Foundation laid for future async implementation
- **Error Handling**: Comprehensive exception handling with recovery

### 4. Performance Optimizations
- **Database Optimizations**:
  - WAL mode for better concurrency
  - Proper indexing for query performance
  - Connection pooling and reuse
  - Batch operations for efficiency

- **API Optimizations**:
  - HTTP session reuse
  - Intelligent retry logic with exponential backoff
  - Rate limiting and throttling
  - Concurrent request processing

- **Memory Management**:
  - Streaming data processing
  - Garbage collection optimization
  - Resource cleanup and management
  - Configurable batch sizes

### 5. Extensibility Features
- **Plugin Architecture**: Easy addition of new *Arr services
- **Analysis Modules**: Pluggable analysis algorithms
- **Export Formats**: Strategy pattern for different output formats
- **Dashboard Components**: Modular dashboard sections

## File Organization Philosophy

### Legacy Compatibility
- **`legacy/`**: Original monolithic scripts for users preferring simple approach
- **`arr_score_exporter.py`**: Main CLI maintaining backward compatibility
- **Configuration**: Both old script variables and new YAML configs supported

### Modern Architecture
- **`src/`**: Clean module organization following Python best practices
- **Separation**: Clear boundaries between data, logic, and presentation
- **Testing**: Comprehensive test coverage with realistic fixtures
- **Documentation**: Extensive documentation for all components

### Development Support
- **`scripts/`**: Development utilities and validation tools
- **`tests/`**: Full test suite with fixtures and mocks
- **`docs/`**: Comprehensive documentation including architecture guides
- **`examples/`**: Real-world usage examples and templates

## Development Workflow

### Code Organization Standards
1. **Module Imports**: Absolute imports from package root
2. **Type Annotations**: Complete type coverage for all public APIs
3. **Documentation**: Comprehensive docstrings for all modules and functions
4. **Error Handling**: Proper exception handling with informative messages
5. **Logging**: Structured logging throughout the application

### Testing Strategy
1. **Unit Tests**: Individual component testing with mocks
2. **Integration Tests**: End-to-end workflow testing
3. **Performance Tests**: Database and API performance validation
4. **Compatibility Tests**: Cross-platform and Python version testing

### Documentation Standards
1. **Architecture Documentation**: High-level design and patterns
2. **API Documentation**: Complete CLI and Python API reference
3. **User Documentation**: Installation, configuration, and usage guides
4. **Developer Documentation**: Contributing guidelines and development setup

## Migration Path

### From Legacy to Enhanced
Users can migrate gradually:
1. **Phase 1**: Continue using legacy scripts in `legacy/` folder
2. **Phase 2**: Adopt YAML configuration with main CLI script
3. **Phase 3**: Utilize enhanced CLI with rich output and dashboards
4. **Phase 4**: Leverage full analysis and historical tracking features

### Backward Compatibility
- Legacy scripts remain fully functional
- Configuration migration tools available
- Data import from CSV to database supported
- Gradual feature adoption without breaking changes

## Future Architecture Considerations

### Scalability Enhancements
- **Async/Await**: Complete migration to async for better performance
- **Distributed Processing**: Multi-node processing capabilities
- **Caching Layer**: Redis integration for distributed caching
- **Database Sharding**: Horizontal scaling for massive libraries

### Advanced Features
- **Machine Learning Integration**: Predictive analytics and recommendations
- **Real-Time Processing**: WebSocket-based live updates
- **API Gateway**: RESTful API for external integrations
- **Multi-Tenant Support**: Support for multiple users and libraries

### Enterprise Features
- **Role-Based Access Control**: User permissions and access management
- **Audit Trail**: Comprehensive activity logging and compliance
- **SSO Integration**: Enterprise authentication integration
- **High Availability**: Clustering and failover capabilities

This enhanced architecture provides a solid foundation for current functionality while enabling future growth and feature expansion.