# Detailed Usage Guide

This guide provides in-depth information about using the *Arr Custom Format Score Exporter scripts.

## Understanding Custom Format Scores

Custom Format scores in Radarr and Sonarr are used to:

1. Identify high-quality media releases
2. Automate upgrading of media files based on quality preferences
3. Apply specific release criteria in quality profiles

The higher the score, the better the release matches your custom format criteria.

## Script Capabilities

### Common Features

Both scripts:
- Connect to *arr APIs securely
- Use multi-threading for faster processing
- Support error handling and logging
- Produce sorted CSV output files
- Map quality profile IDs to human-readable names

### Radarr Script (`export_radarr_scores.py`)

1. **Fetches Quality Profiles**:
   - Retrieves all quality profiles configured in Radarr
   - Maps profile IDs to names for readable output

2. **Collects Movie Data**:
   - Retrieves your entire movie library information
   - Filters to include only movies with files

3. **Parallel Processing**:
   - Collects detailed file information for each movie
   - Uses thread pooling for efficient API requests

4. **Score Calculation**:
   - Extracts custom format scores from movie files
   - Uses direct score value or calculates from individual format matches

5. **CSV Generation**:
   - Creates CSV with movie title, file path, score, and quality profile
   - Sorts by score (highest first) to easily identify best versions

### Sonarr Script (`export_sonarr_scores.py`)

1. **Fetches Quality Profiles**:
   - Retrieves all quality profiles configured in Sonarr
   - Maps profile IDs to names for readable output

2. **Collects Series and Episode Data**:
   - Retrieves all series in your library
   - Fetches all episodes for each series
   - Filters to include only episodes with files

3. **Parallel Processing**:
   - Collects detailed file information for each episode
   - Uses thread pooling for efficient API requests

4. **Score Calculation**:
   - Extracts custom format scores from episode files
   - Uses direct score value or calculates from individual format matches

5. **CSV Generation**:
   - Creates CSV with series title, episode info, file path, score, and quality profile
   - Sorts by series title and episode for easy navigation

## Advanced Configuration

### Performance Considerations

The scripts include several performance-related settings you can adjust:

```python
MAX_WORKERS = 15  # Number of parallel threads for API requests
API_TIMEOUT = 30  # Seconds to wait for API response
REQUEST_DELAY = 0.0  # Delay between API requests (usually not needed)
```

Recommendations:
- For local networks, keep `REQUEST_DELAY` at 0.0
- If your *arr instance is remote or resource-constrained, set `REQUEST_DELAY` to 0.5 or higher
- If you experience timeouts, increase `API_TIMEOUT` to 60 or higher
- Adjust `MAX_WORKERS` based on your system's capabilities:
  - Powerful system, local network: 15-25
  - Average system, local network: 10-15
  - Remote or resource-constrained system: 5-10

### Security Considerations

- The scripts store API keys in plain text. For better security:
  1. Consider using environment variables
  2. Ensure your script files have restricted permissions
  3. Never commit API keys to public repositories

## Output Analysis

### Sample Radarr Output

```
Title,File,Score,Quality Profile
Inception,Inception (2010) [Bluray-1080p][x265][10bit][DTS 5.1],25,HD-1080p
The Matrix,The.Matrix.1999.2160p.UHD.BluRay.REMUX.HDR.HEVC.Atmos-TRiToN.mkv,20,4K Movies
Interstellar,Interstellar (2014) [Bluray-1080p][x264][DTS 5.1],15,HD-1080p
```

### Sample Sonarr Output

```
Series Title,Episode,Episode Title,File,Score,Quality Profile
Breaking Bad,S01E01,Pilot,Breaking.Bad.S01E01.Pilot.2160p.Netflix.WEB-DL.x265.10bit.HDR.DDP5.1-FLUX.mkv,18,TV UHD
Game of Thrones,S08E06,The Iron Throne,Game.of.Thrones.S08E06.The.Iron.Throne.1080p.BluRay.x264-SPARKS.mkv,12,TV HD
Stranger Things,S04E01,Chapter One: The Hellfire Club,Stranger.Things.S04E01.1080p.NF.WEB-DL.DDP5.1.Atmos.x264-TEPES.mkv,10,TV HD
```

## Use Cases

1. **Identify Upgrade Candidates**:
   - Filter your CSV for media with low scores in important profiles
   - Target these for manual or automatic upgrades

2. **Verify Custom Format Rules**:
   - Check if your custom format rules are scoring as expected
   - Make adjustments to your rules if needed

3. **Media Library Analysis**:
   - Track overall quality of your library
   - Generate statistics about your media collection

4. **Backup Preparation**:
   - Identify highest-scoring files to prioritize for backup
   - Ensure your best quality media is preserved

## Common Issues

1. **API Connection Problems**:
   - Verify URL includes http:// or https://
   - Confirm API key is correct and has proper permissions
   - Check if your *arr instance is accessible from the script's network

2. **Timeout Errors**:
   - Increase `API_TIMEOUT` value
   - Decrease `MAX_WORKERS` to reduce concurrent load
   - Check if your *arr instance is under heavy load or limited resources

3. **Missing Scores**:
   - Ensure you have custom formats configured in your *arr application
   - Verify custom formats are assigned to quality profiles
   - Check if media files have been assessed for custom formats

4. **Slow Performance**:
   - Large libraries will naturally take longer to process
   - Try increasing `MAX_WORKERS` if your system can handle it
   - Run during periods of low *arr activity
