# *Arr Custom Format Score Exporter

A set of Python scripts to export custom format scores from Radarr (movies) and Sonarr (TV shows) to CSV files.

## What This Does

These scripts connect to Radarr and Sonarr APIs to export:

- **For Radarr**: Movie titles, file paths, custom format scores, and quality profiles
- **For Sonarr**: Series titles, episode information, file paths, custom format scores, and quality profiles

The output is sorted CSV files that can help you analyze which media files have the highest custom format scores and identify upgrade candidates.

## Requirements

- Python 3.6 or higher
- Radarr v3 and/or Sonarr v3 instances
- API access to your *arr applications

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/arr-score-exporter.git
   cd arr-score-exporter
   ```

2. Install required Python packages:
   ```bash
   pip install requests
   ```

## Configuration

Before running the scripts, you need to configure them with your specific settings:

### Radarr Configuration

Edit `export_radarr_scores.py` and update the following variables:

```python
API_KEY    = "yourapikey"  # Replace with your actual Radarr API Key
RADARR_URL = "http://127.0.0.1:7878" # Your Radarr host:port
OUTPUT_CSV = "radarr_custom_scores.csv"
MAX_WORKERS = 15  # Adjust based on your system capabilities
```

### Sonarr Configuration

Edit `export_sonarr_scores.py` and update the following variables:

```python
SONARR_API_KEY = "yourapikey"  # Replace with your actual Sonarr API Key
SONARR_URL = "http://your.sonarr.host:8989" # Your Sonarr host:port
SONARR_OUTPUT_CSV = "sonarr_custom_scores.csv"
MAX_WORKERS = 15  # Adjust based on your system capabilities
```

## Usage

### Export Radarr Scores

```bash
python export_radarr_scores.py
```

This will:
1. Connect to your Radarr instance
2. Fetch all movies and their file details
3. Calculate custom format scores for each movie file
4. Export the results to `radarr_custom_scores.csv` sorted by score (highest first)

### Export Sonarr Scores

```bash
python export_sonarr_scores.py
```

This will:
1. Connect to your Sonarr instance
2. Fetch all series and their episodes
3. Calculate custom format scores for each episode file
4. Export the results to `sonarr_custom_scores.csv` sorted by series title and episode number

## Performance Tuning

Both scripts support parallel processing to speed up data collection. You can adjust the `MAX_WORKERS` value to control how many parallel requests are made:

- Lower values (5-10) are safer but slower
- Higher values (15-25) are faster but may put more load on your system and *arr instances
- Start with the default of 15 and adjust based on your results

## Output Format

### Radarr CSV Format

The `radarr_custom_scores.csv` file contains the following columns:

- `Title`: Movie title
- `File`: Relative file path
- `Score`: Custom format score
- `Quality Profile`: Quality profile name

### Sonarr CSV Format

The `sonarr_custom_scores.csv` file contains the following columns:

- `Series Title`: TV show title
- `Episode`: Episode identifier (SXXEXX format)
- `Episode Title`: Episode title
- `File`: Relative file path
- `Score`: Custom format score
- `Quality Profile`: Quality profile name

## How It Works

1. The scripts first fetch quality profile mappings to display profile names
2. Then they collect all media items (movies or TV episodes)
3. For each item with files, they fetch detailed file information using parallel processing
4. Custom format scores are extracted from the file details
5. Results are compiled, sorted, and written to CSV files

## Troubleshooting

- If you see timeout errors, try decreasing `MAX_WORKERS` or increasing `API_TIMEOUT`
- Ensure your API key and URL are correctly configured
- Make sure your *arr instances are running and accessible
- Check that your API key has the necessary permissions

## License

[MIT License](LICENSE)

## Acknowledgments

- Radarr and Sonarr development teams for providing comprehensive APIs
- TRaSH Guides for custom formats inspiration

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.
