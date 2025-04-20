# *Arr Custom Format Score Exporter
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A set of Python scripts to export custom format scores from Radarr (movies) and Sonarr (TV shows) to CSV files.

## What This Does

These scripts connect to Radarr and Sonarr APIs to export:

- **For Radarr**: Movie titles, file paths, custom format scores, and quality profiles
- **For Sonarr**: Series titles, episode information, file paths, custom format scores, and quality profiles

The output is sorted CSV files that can help you analyze which media files have the highest custom format scores and identify upgrade candidates.

## Requirements

- Python 3.6 or higher
- Access to Radarr v3+ and/or Sonarr v3+ instances via their API
- API Keys for your *arr applications

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/arr-score-exporter.git # Replace with the actual URL later
    cd arr-score-exporter
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the virtual environment (only needs to be done once)
    python -m venv venv

    # Activate the virtual environment
    # On Windows (cmd.exe/PowerShell):
    .\venv\Scripts\activate
    # On Linux/macOS (bash/zsh):
    source venv/bin/activate
    ```
    *(You should see `(venv)` at the beginning of your terminal prompt)*

3.  **Install required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Before running the scripts, you need to configure them with your specific settings:

Before running the scripts, you need to configure them with your specific *arr instance details and API keys.

Edit the `REQUIRED SETTINGS` section at the top of `export_radarr_scores.py` and/or `export_sonarr_scores.py`:

**For Radarr (`export_radarr_scores.py`):**
```python
RADARR_API_KEY = "YOUR_APP_API_KEY_HERE"  # Replace with your actual Radarr API Key
RADARR_URL     = "http://127.0.0.1:7878" # Replace with your Radarr URL
RADARR_OUTPUT_CSV = "radarr_custom_scores.csv" # Output file name
```

**For Sonarr (`export_sonarr_scores.py`):**
```python
SONARR_API_KEY    = "YOUR_APP_API_KEY_HERE"  # Replace with your actual Sonarr API Key
SONARR_URL        = "http://127.0.0.1:8989" # Replace with your Sonarr URL
SONARR_OUTPUT_CSV = "sonarr_custom_scores.csv" # Output file name
```

## Usage

Ensure your virtual environment is activated before running the scripts (you should see `(venv)` in your prompt).

### Export Radarr Scores

```bash
python export_radarr_scores.py
```
This will connect to Radarr, fetch movie data, calculate scores, and save the results to the configured CSV file (default: `radarr_custom_scores.csv`), sorted by score (highest first).

### Export Sonarr Scores

```bash
python export_sonarr_scores.py
```
This will connect to Sonarr, fetch series/episode data, calculate scores, and save the results to the configured CSV file (default: `sonarr_custom_scores.csv`), sorted by series title and episode number.

## Performance Tuning

Both scripts use parallel processing (`MAX_WORKERS`) to speed up fetching file details. You can adjust this value in the configuration section of each script based on your system's performance and the responsiveness of your *arr instances. See the comments in the scripts for guidance.

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
- Check that your API key has the necessary permissions.
- For more detailed information, see the [Detailed Usage Guide](USAGE-GUIDE.md).

## License

[MIT License](LICENSE)

## Acknowledgments

- Radarr and Sonarr development teams for providing comprehensive APIs.
- [TRaSH Guides](https://trash-guides.info/) for custom formats inspiration.

## Contributing

Contributions, issues, and feature requests are welcome! Please check the contribution guidelines (if available) or open an issue to discuss changes.
