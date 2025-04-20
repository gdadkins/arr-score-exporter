# Project Structure

This document outlines the recommended structure for the *Arr Custom Format Score Exporter project repository.

## Repository Layout

```
arr-score-exporter/
├── LICENSE                  # MIT License file
├── README.md                # Primary project documentation
├── USAGE_GUIDE.md           # Detailed usage instructions 
├── requirements.txt         # Python dependencies
├── export_radarr_scores.py  # Radarr script
├── export_sonarr_scores.py  # Sonarr script
├── .gitignore               # Git ignore file
└── examples/                # Example output and configuration
    ├── example_radarr.csv   # Sample Radarr output
    ├── example_sonarr.csv   # Sample Sonarr output
    └── config_examples.md   # Example configurations
```

## File Descriptions

### Core Files

- **export_radarr_scores.py**: Python script for exporting custom format scores from Radarr
- **export_sonarr_scores.py**: Python script for exporting custom format scores from Sonarr

### Documentation Files

- **README.md**: Main project documentation with basic instructions
- **USAGE_GUIDE.md**: Detailed instructions and explanation of features
- **LICENSE**: MIT License file
- **PROJECT_STRUCTURE.md**: This document

### Configuration Files

- **requirements.txt**: List of Python package dependencies

### Example Files

- **examples/example_radarr.csv**: Sample output from the Radarr script
- **examples/example_sonarr.csv**: Sample output from the Sonarr script
- **examples/config_examples.md**: Example configurations for different scenarios

## Future Expansion

The project structure allows for future expansion with:

- Additional scripts for other *arr applications (Lidarr, Readarr, etc.)
- Visualization tools for the exported data
- Integration scripts for other media management tools

## Organization Best Practices

1. **Keep Scripts Separate**: Maintain separate scripts for each application to allow independent updates
2. **Centralize Documentation**: Keep all documentation in the root directory for easy access
3. **Version Control**: Use meaningful commit messages describing changes to each file
4. **Example Data**: Include anonymized example data to help users understand the output
