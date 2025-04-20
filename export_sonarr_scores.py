#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sonarr Custom Format Score Exporter

This script connects to a Sonarr instance using its API, fetches all series and
their episodes, retrieves details about the episode files (including custom
format scores and quality profiles), and exports this information to a CSV file.

Requires:
    - Python 3.6+
    - `requests` library (install via pip: pip install requests)
    - Access to a Sonarr v3+ instance with API key.
"""
import requests
import csv
import json
import time
import concurrent.futures # For parallel processing

# --- Configuration ---
# ┌─────────────────────────────┐
# │     REQUIRED SETTINGS       │
# └─────────────────────────────┘
SONARR_API_KEY    = "YOUR_APP_API_KEY_HERE"  # Replace with your actual Sonarr API Key
SONARR_URL        = "http://127.0.0.1:8989" # Replace with your Sonarr URL (e.g., http://sonarr:8989 or https://sonarr.domain.com)
SONARR_OUTPUT_CSV = "sonarr_custom_scores.csv" # Name of the output CSV file

# ┌─────────────────────────────┐
# │    PERFORMANCE & TIMING     │
# └─────────────────────────────┘
# Number of parallel workers to fetch file details.
# Adjust based on your system & Sonarr's responsiveness.
# Start lower (e.g., 5-10) and increase if your system handles it well.
# Too high might overload Sonarr or cause rate-limiting issues.
MAX_WORKERS = 15

# Seconds to wait for a response from the Sonarr API for each request.
API_TIMEOUT = 30

# Delay in seconds between consecutive API requests made by the main thread
# or within the same worker thread (if applicable).
# Useful for very slow servers or strict rate limiting. Keep at 0.0 for most cases.
REQUEST_DELAY = 0.0

# --- Constants ---
# (No user-configurable constants currently)

# --- Helper Functions ---

def make_api_request(base_url, api_key, endpoint, params=None, session=None):
    """
    Makes an API request to the specified endpoint with error handling.

    Args:
        base_url (str): The base URL of the Radarr/Sonarr instance.
        api_key (str): The API key for authentication.
        endpoint (str): The API endpoint (e.g., '/api/v3/series').
        params (dict, optional): Query parameters for the request. Defaults to None.
        session (requests.Session, optional): A requests session object to use. Defaults to None.

    Returns:
        dict or None: The JSON response as a dictionary if successful, None otherwise.
    """
    if params is None:
        params = {}
    headers = {"X-Api-Key": api_key} # Use header for API key - more standard
    url = f"{base_url.rstrip('/')}{endpoint}" # Ensure no double slashes
    requester = session or requests # Use provided session or default requests module
    time.sleep(REQUEST_DELAY) # Apply delay before each request
    try:
        r = requester.get(url, params=params, headers=headers, timeout=API_TIMEOUT)
        r.raise_for_status() # Raises HTTPError for 4xx/5xx responses
        return r.json()
    except requests.exceptions.Timeout:
        print(f"ERROR: Timeout connecting to {url}")
    except requests.exceptions.HTTPError as e:
        # Log non-404 errors, as 404 might be expected in some checks
        if e.response.status_code != 404:
            print(f"ERROR: HTTP Error {e.response.status_code} for {url}")
            # print(f"       Response: {e.response.text[:500]}...") # Uncomment for detailed API errors
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed request to {url}: {e}")
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON response from {url}. Response: {r.text[:500]}...")
    return None # Indicate failure

def write_csv(rows, output_filename, fieldnames):
    """
    Writes the processed data rows to a CSV file.

    Args:
        rows (list): A list of dictionaries, where each dictionary represents a row.
        output_filename (str): The path to the output CSV file.
        fieldnames (list): A list of strings representing the CSV header columns.
    """
    if not rows:
        print("INFO: No data to write to CSV.")
        return

    print(f"\nINFO: Writing {len(rows)} entries to {output_filename}...")
    try:
        with open(output_filename, "w", newline="", encoding="utf-8") as f:
            # Ignore extra fields in case the dict has more keys than fieldnames
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
        print(f"INFO: Successfully wrote data to {output_filename}")
    except IOError as e:
        print(f"ERROR: Could not write to CSV file {output_filename}: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during CSV writing: {e}")

# --- Sonarr Specific Functions ---

def get_quality_profile_map(base_url, api_key, session):
    """
    Fetches Sonarr quality profiles and returns a map of ID to Name.

    Args:
        base_url (str): Sonarr base URL.
        api_key (str): Sonarr API key.
        session (requests.Session): Requests session object.

    Returns:
        dict: A dictionary mapping quality profile ID (int) to name (str).
              Returns an empty dict if fetching fails.
    """
    print("INFO: Fetching Sonarr quality profile mapping...")
    endpoint = "/api/v3/qualityprofile"
    profiles = make_api_request(base_url, api_key, endpoint, session=session)
    if profiles:
        profile_map = {p['id']: p['name'] for p in profiles if 'id' in p and 'name' in p}
        print(f"INFO: Successfully fetched {len(profile_map)} quality profiles.")
        return profile_map
    else:
        print("ERROR: Failed to fetch quality profiles. Profile names will be missing.")
        return {} # Return empty dict on failure

def get_all_sonarr_series(base_url, api_key, session):
    """
    Fetches all series from Sonarr.

    Args:
        base_url (str): Sonarr base URL.
        api_key (str): Sonarr API key.
        session (requests.Session): Requests session object.

    Returns:
        dict or None: A map of seriesId -> {'title': seriesTitle, 'qualityProfileId': profileId}
                      if successful, None otherwise.
    """
    print(f"INFO: Fetching all series from Sonarr at {base_url}...")
    endpoint = "/api/v3/series"
    series_data = make_api_request(base_url, api_key, endpoint, session=session)
    if series_data is not None:
        print(f"INFO: Successfully fetched {len(series_data)} series.")
        # Create a map: seriesId -> {'title': seriesTitle, 'qualityProfileId': profileId}
        series_map = {}
        for s in series_data:
            if 'id' in s and 'title' in s:
                series_map[s['id']] = {
                    'title': s['title'],
                    'qualityProfileId': s.get('qualityProfileId') # Use .get for safety if key is missing
                }
            else:
                print(f"WARNING: Skipping series entry due to missing 'id' or 'title': {s}")
        return series_map
    else:
        print("ERROR: Failed to fetch series.")
        return None

def get_sonarr_episodes_for_series(base_url, api_key, series_id, session):
    """
    Fetches all episodes for a specific series ID from Sonarr.

    Args:
        base_url (str): Sonarr base URL.
        api_key (str): Sonarr API key.
        series_id (int): The ID of the series to fetch episodes for.
        session (requests.Session): Requests session object.

    Returns:
        list or None: A list of episode dictionaries if successful, None otherwise.
    """
    endpoint = "/api/v3/episode"
    params = {"seriesId": series_id}
    # Use the session for potentially faster connection reuse
    return make_api_request(base_url, api_key, endpoint, params=params, session=session)

# --- Function to fetch details for ONE file (will be run in threads) ---
def fetch_single_episode_file_details(args):
    """
    Fetches details for a single episode file ID using the provided session.
    Designed to be called by ThreadPoolExecutor.

    Args:
        args (tuple): A tuple containing (base_url, api_key, episode_file_id, session).

    Returns:
        tuple: (episode_file_id, details_dict or None)
    """
    base_url, api_key, episode_file_id, session = args
    endpoint = f"/api/v3/episodeFile/{episode_file_id}"
    # Use the passed session for potential connection reuse within threads
    details = make_api_request(base_url, api_key, endpoint, session=session)
    return episode_file_id, details # Return ID too, to match results later

# --- Main Processing Function (Parallel Episode File Fetching) ---
def process_sonarr_series_and_scores_parallel(series_map, base_url, api_key, quality_profile_map):
    """
    Processes series, fetches episodes, fetches file details in parallel, extracts scores & profiles.

    Args:
        series_map (dict): Map of seriesId -> {'title': ..., 'qualityProfileId': ...}.
        base_url (str): Sonarr base URL.
        api_key (str): Sonarr API key.
        quality_profile_map (dict): Map of quality profile IDs to names.

    Returns:
        list: A list of dictionaries, each containing processed episode info,
              sorted by Series Title, then Episode. Returns empty list on failure or no data.
    """
    if not series_map:
        print("INFO: No series data provided for processing.")
        return []

    start_time = time.time()
    episodes_to_process = [] # List to hold (episode_info_dict, episode_file_id) tuples
    total_series = len(series_map)
    processed_series_count = 0
    total_episodes_found = 0

    print("\nINFO: Phase 1: Fetching episode data for all series (sequentially per series)...")
    # Use a single session for fetching episode lists for better connection reuse
    with requests.Session() as session:
        for series_id, series_info in series_map.items():
            series_title = series_info.get('title', f"Unknown Series (ID: {series_id})")
            series_quality_profile_id = series_info.get('qualityProfileId') # Get profile ID for this series

            processed_series_count += 1
            # Print progress periodically
            if processed_series_count % 20 == 0 or processed_series_count == total_series:
                print(f"  Fetching episodes for Series {processed_series_count}/{total_series}: {series_title}...")

            episodes = get_sonarr_episodes_for_series(base_url, api_key, series_id, session)

            if episodes is None:
                print(f"WARNING: Failed to fetch episodes for series '{series_title}' (ID: {series_id}). Skipping this series.")
                continue # Skip to the next series if fetching episodes fails

            if not isinstance(episodes, list):
                print(f"WARNING: Unexpected data format for episodes of series '{series_title}' (ID: {series_id}). Expected list, got {type(episodes)}. Skipping.")
                continue

            series_episode_count = 0
            for episode in episodes:
                # Ensure episode is a dictionary and has the necessary keys
                if isinstance(episode, dict) and episode.get("hasFile") and episode.get("episodeFileId", 0) > 0:
                    episode_file_id = episode["episodeFileId"]
                    season_num = episode.get("seasonNumber", 0)
                    episode_num = episode.get("episodeNumber", 0)

                    # Store essential info needed *after* file details are fetched
                    episode_info = {
                        "Series Title": series_title,
                        "Episode": f"S{season_num:02d}E{episode_num:02d}", # Formatted episode identifier
                        "Episode Title": episode.get("title", "N/A"),
                        "QualityProfileId": series_quality_profile_id, # Store the series' profile ID
                        "OriginalEpisodeFileId": episode_file_id # Keep for matching later if needed
                    }
                    episodes_to_process.append((episode_info, episode_file_id))
                    series_episode_count += 1

            total_episodes_found += series_episode_count
            # print(f"DEBUG: Found {series_episode_count} episodes with files for series '{series_title}'.") # Optional debug

    print(f"\nINFO: Phase 1 completed. Found {len(episodes_to_process)} episodes with files across {total_series} series.")
    if not episodes_to_process:
        print("INFO: No episodes with files found to process further.")
        return []

    print(f"\nINFO: Phase 2: Fetching {len(episodes_to_process)} episode file details using up to {MAX_WORKERS} parallel workers...")

    file_details_map = {} # Dictionary to store results: episode_file_id -> details_dict
    tasks = []
    # Use one session for all threads in this phase for potential connection reuse
    with requests.Session() as session:
        # Prepare arguments for each task
        for _, episode_file_id in episodes_to_process:
            tasks.append((base_url, api_key, episode_file_id, session))

        processed_count = 0
        # Use ThreadPoolExecutor to run fetch_single_episode_file_details concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Create a mapping from future object to the original episode_file_id for error reporting
            future_to_id = {executor.submit(fetch_single_episode_file_details, task): task[2] for task in tasks}

            for future in concurrent.futures.as_completed(future_to_id):
                original_id = future_to_id[future]
                try:
                    # Result is (episode_file_id, details_dict or None)
                    file_id, details = future.result()
                    if details: # Store only if fetch was successful
                        file_details_map[file_id] = details
                    # else: Fetch failed, error already printed by make_api_request

                except Exception as exc:
                    print(f'WARNING: Episode file ID {original_id} generated an exception during fetch: {exc}')

                processed_count += 1
                # Print progress periodically
                if processed_count % 100 == 0 or processed_count == len(episodes_to_process):
                    print(f"  Fetched details for {processed_count}/{len(episodes_to_process)} files...")


    print(f"\nINFO: Phase 2 completed. Successfully fetched details for {len(file_details_map)} files.")

    print("\nINFO: Phase 3: Processing results, calculating scores, and adding profile names...")
    rows = []
    processed_results_count = 0
    skipped_count = 0
    for episode_info, episode_file_id in episodes_to_process:
        file_details = file_details_map.get(episode_file_id) # Get fetched details using ID

        if file_details:
            processed_results_count +=1
            relative_path = file_details.get("relativePath", "N/A")
            total_score = 0

            # --- Score Calculation Logic ---
            # Sonarr API v3+ usually provides 'customFormatScore' directly in episodeFile details.
            # Fallback to summing 'score' from 'customFormats' list if needed.

            # Method 1: Try the direct 'customFormatScore' field
            total_score = file_details.get("customFormatScore", 0)

            # Method 2: Fallback if score is 0 or field missing
            if total_score == 0:
                custom_formats_list = file_details.get("customFormats")
                if isinstance(custom_formats_list, list): # Check if it's a list
                    try:
                        # Ensure cf is a dictionary and has 'score' before summing
                        current_sum = sum(cf.get('score', 0) for cf in custom_formats_list if isinstance(cf, dict))
                        if current_sum > 0:
                            # print(f"DEBUG: Using summed score {current_sum} for {episode_info['Series Title']} {episode_info['Episode']}") # Optional debug
                            total_score = current_sum
                    except TypeError as e:
                        print(f"WARNING: Type error summing scores for {episode_info['Series Title']} {episode_info['Episode']} (File ID: {episode_file_id}). Formats: {custom_formats_list}. Error: {e}")
                        total_score = 0 # Reset on error
                # else:
                    # print(f"DEBUG: No 'customFormats' list found or not a list for {episode_info['Series Title']} {episode_info['Episode']}") # Optional debug


            # --- Quality Profile Lookup ---
            # Use the profile ID stored from the series info earlier
            profile_id = episode_info.get("QualityProfileId")
            profile_name = quality_profile_map.get(profile_id, f"Unknown ID: {profile_id}" if profile_id else "N/A")

            # --- Append Row ---
            rows.append({
                "Series Title": episode_info["Series Title"],
                "Episode": episode_info["Episode"],
                "Episode Title": episode_info["Episode Title"],
                "File": relative_path, # Get file path from the detailed file info
                "Score": total_score,
                "Quality Profile": profile_name # Add the profile name
            })
        else:
            # Details couldn't be fetched for this file_id, skip it.
            skipped_count += 1
            # print(f"DEBUG: Skipping episode '{episode_info['Series Title']} {episode_info['Episode']}' as file details (ID: {episode_file_id}) were not fetched.")

    end_time = time.time()
    print(f"\nINFO: Phase 3 completed. Processed {processed_results_count} results. Skipped {skipped_count} due to missing details.")
    print(f"INFO: Total processing time: {end_time - start_time:.2f} seconds.")

    if not rows:
        print("INFO: No episodes with processable file details found after processing.")
        return []

    # Sort by Series Title (ascending), then by Episode identifier (ascending)
    print("\nINFO: Sorting results by Series Title, then Episode...")
    # The SxxExx format sorts correctly lexicographically
    return sorted(rows, key=lambda r: (r["Series Title"], r["Episode"]))


# --- Main Execution Logic ---
if __name__ == "__main__":
    print("\n--- Running Sonarr Score & Profile Export (Parallel Version) ---")

    # Basic configuration validation
    if not SONARR_URL.startswith("http://") and not SONARR_URL.startswith("https://"):
        print(f"ERROR: Sonarr URL '{SONARR_URL}' seems invalid. Please include http:// or https://")
        exit(1) # Exit if URL is fundamentally wrong
    if not SONARR_API_KEY or SONARR_API_KEY == "YOUR_APP_API_KEY_HERE":
        print(f"ERROR: Sonarr API Key is missing or still set to the placeholder value.")
        print(f"       Please update SONARR_API_KEY in the script.")
        exit(1) # Exit if API key is missing

    all_sonarr_series = None
    quality_profile_map = {}
    # Use a requests Session for potential keep-alive benefits across initial calls
    with requests.Session() as main_session:
        quality_profile_map = get_quality_profile_map(SONARR_URL, SONARR_API_KEY, main_session)
        # Only proceed if we could fetch profiles (basic connectivity check)
        if quality_profile_map is not None: # Check if it's not None (even if empty)
            all_sonarr_series = get_all_sonarr_series(SONARR_URL, SONARR_API_KEY, main_session)
        else:
             print("ERROR: Could not fetch quality profiles, cannot proceed.")


    if all_sonarr_series: # Check if series map is not None and not empty
        # Call the parallel processing function, passing the profile map
        sonarr_scored_list = process_sonarr_series_and_scores_parallel(
            all_sonarr_series, SONARR_URL, SONARR_API_KEY, quality_profile_map
        )

        if sonarr_scored_list:
            # Define fieldnames for CSV header
            sonarr_fieldnames = ["Series Title", "Episode", "Episode Title", "File", "Score", "Quality Profile"]
            write_csv(sonarr_scored_list, SONARR_OUTPUT_CSV, sonarr_fieldnames)
        else:
            print("INFO: Processing yielded no data to write to CSV.")
    elif quality_profile_map is not None: # Only print this if profile fetch didn't already fail
        print("ERROR: Could not retrieve Sonarr series list. Exiting Sonarr export.")

    print("\n--- Sonarr Score & Profile Export Finished ---")
