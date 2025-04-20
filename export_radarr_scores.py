#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radarr Custom Format Score Exporter

This script connects to a Radarr instance using its API, fetches all movies,
retrieves details about their associated files (including custom format scores
and quality profiles), and exports this information to a CSV file.

Requires:
    - Python 3.6+
    - `requests` library (install via pip: pip install requests)
    - Access to a Radarr v3+ instance with API key.
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
RADARR_API_KEY = "YOUR_APP_API_KEY_HERE"  # Replace with your actual Radarr API Key
RADARR_URL     = "http://127.0.0.1:7878" # Replace with your Radarr URL (e.g., http://radarr:7878 or https://radarr.domain.com)
RADARR_OUTPUT_CSV = "radarr_custom_scores.csv" # Name of the output CSV file

# ┌─────────────────────────────┐
# │    PERFORMANCE & TIMING     │
# └─────────────────────────────┘
# Number of parallel workers to fetch file details.
# Adjust based on your system & Radarr's responsiveness.
# Start lower (e.g., 5-10) and increase if your system handles it well.
# Too high might overload Radarr or cause rate-limiting issues.
MAX_WORKERS = 15

# Seconds to wait for a response from the Radarr API for each request.
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
        endpoint (str): The API endpoint (e.g., '/api/v3/movie').
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
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore') # Ignore extra fields if any
            writer.writeheader()
            writer.writerows(rows)
        print(f"INFO: Successfully wrote data to {output_filename}")
    except IOError as e:
        print(f"ERROR: Could not write to CSV file {output_filename}: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during CSV writing: {e}")


# --- Radarr Specific Functions ---

def get_quality_profile_map(base_url, api_key, session):
    """
    Fetches Radarr quality profiles and returns a map of ID to Name.

    Args:
        base_url (str): Radarr base URL.
        api_key (str): Radarr API key.
        session (requests.Session): Requests session object.

    Returns:
        dict: A dictionary mapping quality profile ID (int) to name (str).
              Returns an empty dict if fetching fails.
    """
    print("INFO: Fetching Radarr quality profile mapping...")
    endpoint = "/api/v3/qualityprofile"
    profiles = make_api_request(base_url, api_key, endpoint, session=session)
    if profiles:
        profile_map = {p['id']: p['name'] for p in profiles if 'id' in p and 'name' in p}
        print(f"INFO: Successfully fetched {len(profile_map)} quality profiles.")
        return profile_map
    else:
        print("ERROR: Failed to fetch quality profiles. Profile names will be missing.")
        return {}

def get_all_movies(base_url, api_key, session):
    """
    Fetches all movies from Radarr.

    Args:
        base_url (str): Radarr base URL.
        api_key (str): Radarr API key.
        session (requests.Session): Requests session object.

    Returns:
        list or None: A list of movie dictionaries if successful, None otherwise.
    """
    print(f"INFO: Fetching all movies from Radarr at {base_url}...")
    endpoint = "/api/v3/movie"
    movies_data = make_api_request(base_url, api_key, endpoint, session=session)
    if movies_data is not None:
        print(f"INFO: Successfully fetched {len(movies_data)} movies.")
        return movies_data
    else:
        print("ERROR: Failed to fetch movies.")
        return None

# --- Function to fetch details for ONE file (will be run in threads) ---
def fetch_single_movie_file_details(args):
    """
    Fetches details for a single movie file ID using the provided session.
    Designed to be called by ThreadPoolExecutor.

    Args:
        args (tuple): A tuple containing (base_url, api_key, movie_file_id, session).

    Returns:
        tuple: (movie_file_id, details_dict or None)
    """
    base_url, api_key, movie_file_id, session = args
    endpoint = f"/api/v3/movieFile/{movie_file_id}"
    # Use the passed session for potential connection reuse within threads
    details = make_api_request(base_url, api_key, endpoint, session=session)
    return movie_file_id, details # Return ID too, to match results later


# --- Main Processing Function (Parallel Version) ---
def process_movies_and_scores_parallel(movies, base_url, api_key, quality_profile_map):
    """
    Processes movies, fetches file details in parallel, extracts scores & profiles.

    Args:
        movies (list): List of movie dictionaries from Radarr API.
        base_url (str): Radarr base URL.
        api_key (str): Radarr API key.
        quality_profile_map (dict): Map of quality profile IDs to names.

    Returns:
        list: A list of dictionaries, each containing processed movie info,
              sorted by score (descending). Returns empty list on failure or no data.
    """
    if not movies:
        print("INFO: No movie data provided for processing.")
        return []

    start_time = time.time()
    files_to_process = [] # List to hold (movie_info_dict, movie_file_id) tuples

    print("\nINFO: Phase 1: Identifying movies with files and extracting initial info...")
    processed_count = 0
    for movie in movies:
        processed_count += 1
        movie_file_summary = movie.get("movieFile")
        # Ensure movie has a file and the file summary exists
        if movie.get("hasFile") and movie_file_summary and isinstance(movie_file_summary, dict):
            movie_file_id = movie_file_summary.get("id")
            quality_profile_id = movie.get("qualityProfileId") # Get profile ID from the movie object

            if movie_file_id:
                # Store essential info needed *after* file details are fetched
                movie_info = {
                    "Title": movie.get("title", "N/A"),
                    # Get path from summary - often sufficient and available earlier
                    "File": movie_file_summary.get("relativePath", "N/A"),
                    "QualityProfileId": quality_profile_id, # Store the ID
                    "OriginalMovieFileId": movie_file_id # For matching later if needed
                }
                files_to_process.append((movie_info, movie_file_id))
            # else:
            #    print(f"DEBUG: Movie '{movie.get('title', 'N/A')}' has file but no movieFile ID found in summary. Skipping.")
        # else:
            # print(f"DEBUG: Skipping movie '{movie.get('title', 'N/A')}' - No file or missing file summary.")

    total_movies = len(movies)
    print(f"INFO: Phase 1 completed. Identified {len(files_to_process)} movies with file IDs out of {total_movies} total movies.")
    if not files_to_process:
        print("INFO: No movies with processable files found.")
        return []

    print(f"\nINFO: Phase 2: Fetching {len(files_to_process)} movie file details using up to {MAX_WORKERS} parallel workers...")

    file_details_map = {} # Dictionary to store results: movie_file_id -> details_dict
    tasks = []
    # Use one session for all threads in this phase for potential connection reuse
    with requests.Session() as session:
        # Prepare arguments for each task
        for _, movie_file_id in files_to_process:
            tasks.append((base_url, api_key, movie_file_id, session))

        processed_count = 0
        # Use ThreadPoolExecutor to run fetch_single_movie_file_details concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Create a mapping from future object to the original movie_file_id for error reporting
            future_to_id = {executor.submit(fetch_single_movie_file_details, task): task[2] for task in tasks}

            for future in concurrent.futures.as_completed(future_to_id):
                original_id = future_to_id[future]
                try:
                    # Result is (movie_file_id, details_dict or None)
                    file_id, details = future.result()
                    if details: # Store only if fetch was successful
                        file_details_map[file_id] = details
                    # else: Fetch failed, error already printed by make_api_request

                except Exception as exc:
                    print(f'WARNING: Movie file ID {original_id} generated an exception during fetch: {exc}')

                processed_count += 1
                # Print progress periodically
                if processed_count % 50 == 0 or processed_count == len(files_to_process):
                    print(f"  Fetched details for {processed_count}/{len(files_to_process)} files...")

    print(f"\nINFO: Phase 2 completed. Successfully fetched details for {len(file_details_map)} files.")

    print("\nINFO: Phase 3: Processing results, calculating scores, and adding profile names...")
    rows = []
    processed_results_count = 0
    skipped_count = 0
    for movie_info, movie_file_id in files_to_process:
        file_details = file_details_map.get(movie_file_id) # Get fetched details using ID

        if file_details:
            processed_results_count += 1
            total_score = 0 # Default score

            # --- Score Calculation Logic ---
            # Radarr API v3+ usually provides 'customFormatScore' directly in movieFile details.
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
                            # print(f"DEBUG: Using summed score {current_sum} for {movie_info['Title']}") # Optional debug
                            total_score = current_sum
                    except TypeError as e:
                        print(f"WARNING: Type error summing scores for '{movie_info['Title']}' (File ID: {movie_file_id}). Formats list: {custom_formats_list}. Error: {e}")
                        total_score = 0 # Reset score on error
                # else:
                    # print(f"DEBUG: No 'customFormats' list found or not a list for {movie_info['Title']}") # Optional debug

            # --- Quality Profile Lookup ---
            profile_id = movie_info.get("QualityProfileId")
            profile_name = quality_profile_map.get(profile_id, f"Unknown ID: {profile_id}" if profile_id else "N/A")

            # --- Append Row ---
            rows.append({
                "Title": movie_info["Title"],
                "File": movie_info["File"], # Use path from summary info collected earlier
                "Score": total_score,
                "Quality Profile": profile_name # Add the profile name
            })
        else:
            # Details couldn't be fetched for this file_id, skip it.
            skipped_count += 1
            # print(f"DEBUG: Skipping movie '{movie_info['Title']}' as file details (ID: {movie_file_id}) were not fetched.")

    end_time = time.time()
    print(f"\nINFO: Phase 3 completed. Processed {processed_results_count} results. Skipped {skipped_count} due to missing details.")
    print(f"INFO: Total processing time: {end_time - start_time:.2f} seconds.")

    if not rows:
        print("INFO: No movies with processable file details found after processing.")
        return []

    # Sort by Score (descending), then by Title (ascending) as a secondary sort key
    print("\nINFO: Sorting results by Score (descending), then Title...")
    return sorted(rows, key=lambda r: (-r["Score"], r["Title"]))


# --- Main Execution Logic ---
if __name__ == "__main__":
    print("\n--- Running Radarr Score & Profile Export (Parallel Version) ---")

    # Basic configuration validation
    if not RADARR_URL.startswith("http://") and not RADARR_URL.startswith("https://"):
        print(f"ERROR: Radarr URL '{RADARR_URL}' seems invalid. Please include http:// or https://")
        exit(1) # Exit if URL is fundamentally wrong
    if not RADARR_API_KEY or RADARR_API_KEY == "YOUR_APP_API_KEY_HERE":
        print(f"ERROR: Radarr API Key is missing or still set to the placeholder value.")
        print(f"       Please update RADARR_API_KEY in the script.")
        exit(1) # Exit if API key is missing

    all_movies = None
    quality_profile_map = {}
    # Use a requests Session for potential keep-alive benefits across initial calls
    with requests.Session() as main_session:
        quality_profile_map = get_quality_profile_map(RADARR_URL, RADARR_API_KEY, main_session)
        # Only proceed if we could fetch profiles (basic connectivity check)
        if quality_profile_map is not None: # Check if it's not None (even if empty)
             all_movies = get_all_movies(RADARR_URL, RADARR_API_KEY, main_session)
        else:
            print("ERROR: Could not fetch quality profiles, cannot proceed.")


    if all_movies:
        # Call the parallel processing function, passing the profile map
        scored_list = process_movies_and_scores_parallel(all_movies, RADARR_URL, RADARR_API_KEY, quality_profile_map)

        if scored_list:
            # Define fieldnames for CSV header
            radarr_fieldnames = ["Title", "File", "Score", "Quality Profile"]
            write_csv(scored_list, RADARR_OUTPUT_CSV, radarr_fieldnames)
        else:
            print("INFO: Processing yielded no data to write to CSV.")
    elif quality_profile_map is not None: # Only print this if profile fetch didn't already fail
        print("ERROR: Could not retrieve Radarr movie list. Exiting Radarr export.")

    print("\n--- Radarr Score & Profile Export Finished ---")
