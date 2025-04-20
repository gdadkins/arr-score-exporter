import requests
import csv
import json
import time
import concurrent.futures # Import for threading

# ─── CONFIG ─────────────────────────────────────────────────────────────────
SONARR_API_KEY = "YOUR_APP_API_KEY_HERE"  # Replace with your actual Sonarr API Key
SONARR_URL = "http://127.0.0.1:8989" # Replace with your actual Sonarr URL/Port (DEFAULT is 8989)
SONARR_OUTPUT_CSV = "sonarr_custom_scores.csv"
# --- Performance Tuning ---
# Number of parallel workers to fetch file details. Adjust based on your system & Sonarr's responsiveness.
# Start lower (e.g., 5-10) and increase if your system handles it well. Too high might overload Sonarr.
MAX_WORKERS = 15
# ─────────────────────────────────────────────────────────────────────────────

API_TIMEOUT = 30 # Seconds to wait for API response
REQUEST_DELAY = 0.0 # Keep at 0 for maximum speed on local network

# --- Helper Functions ---

def make_api_request(base_url, api_key, endpoint, params=None, session=None):
    """Helper function to make API requests with error handling using a session."""
    if params is None:
        params = {}
    params["apikey"] = api_key
    url = f"{base_url}{endpoint}"
    requester = session or requests # Use provided session or default requests
    try:
        r = requester.get(url, params=params, timeout=API_TIMEOUT)
        r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return r.json()
    except requests.exceptions.Timeout:
        print(f"Error: Timeout connecting to {url}")
    except requests.exceptions.HTTPError as e:
        # Don't print every 404 if just checking optional data
        if e.response.status_code != 404:
            print(f"Error: HTTP Error {e.response.status_code} for {url}")
            # print(f"Response: {e.response.text}") # Uncomment for detailed API error messages
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed request to {url}: {e}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON response from {url}")
    return None # Indicate failure

def write_csv(rows, output_filename, fieldnames):
    """Writes the processed data to a CSV file."""
    if not rows:
        print("No data to write to CSV.")
        return

    print(f"\nWriting {len(rows)} entries to {output_filename}...")
    try:
        with open(output_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Successfully wrote data to {output_filename}")
    except IOError as e:
        print(f"Error writing to CSV file {output_filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV writing: {e}")

# --- Sonarr Specific Functions ---

def get_quality_profile_map(base_url, api_key, session):
    """Fetches quality profiles and returns a map of ID to Name."""
    print("Fetching quality profile mapping...")
    endpoint = "/api/v3/qualityprofile"
    profiles = make_api_request(base_url, api_key, endpoint, session=session)
    if profiles:
        profile_map = {p['id']: p['name'] for p in profiles if 'id' in p and 'name' in p}
        print(f"Successfully fetched {len(profile_map)} quality profiles.")
        return profile_map
    else:
        print("Error: Failed to fetch quality profiles. Profile names will be missing.")
        return {}

def get_all_sonarr_series(base_url, api_key, session):
    """Fetches all series from Sonarr, returning a map including title and quality profile ID."""
    print(f"Fetching all series from Sonarr at {base_url}...")
    endpoint = "/api/v3/series"
    series_data = make_api_request(base_url, api_key, endpoint, session=session)
    if series_data is not None:
        print(f"Successfully fetched {len(series_data)} series.")
        # Create a map: seriesId -> {'title': seriesTitle, 'qualityProfileId': profileId}
        series_map = {}
        for s in series_data:
            if 'id' in s and 'title' in s:
                series_map[s['id']] = {
                    'title': s['title'],
                    'qualityProfileId': s.get('qualityProfileId') # Use .get for safety
                }
        return series_map
    else:
        print("Failed to fetch series.")
        return None

def get_sonarr_episodes_for_series(base_url, api_key, series_id, session):
    """Fetches all episodes for a specific series ID from Sonarr."""
    endpoint = "/api/v3/episode"
    params = {"seriesId": series_id}
    # Use the session for potentially faster connection reuse
    return make_api_request(base_url, api_key, endpoint, params, session=session)

# --- Function to fetch details for ONE file (will be run in threads) ---
def fetch_single_episode_file_details(args):
    """Fetches details for a single episode file ID. Designed for ThreadPoolExecutor."""
    base_url, api_key, episode_file_id, session = args
    endpoint = f"/api/v3/episodeFile/{episode_file_id}"
    # Use the session for potentially faster connection reuse within threads
    details = make_api_request(base_url, api_key, endpoint, session=session)
    return episode_file_id, details # Return ID too, to match results later

# --- Main Processing Function (Heavily Modified) ---
def process_sonarr_series_and_scores_parallel(series_map, base_url, api_key, quality_profile_map):
    """Processes series, fetches episodes, fetches file details in parallel, extracts scores and profile."""
    if not series_map:
        print("No series data to process.")
        return []

    start_time = time.time()
    episodes_to_process = [] # List to hold (episode_info, episode_file_id) tuples
    total_series = len(series_map)
    processed_series_count = 0

    print("Phase 1: Fetching all episode data (sequentially per series)...")
    # Use a session for potential connection reuse benefits
    with requests.Session() as session:
        for series_id, series_info in series_map.items():
            series_title = series_info['title']
            series_quality_profile_id = series_info.get('qualityProfileId') # Get profile ID for this series

            processed_series_count += 1
            if processed_series_count % 20 == 0 or processed_series_count == total_series:
                print(f"  Fetching episodes for Series {processed_series_count}/{total_series}: {series_title}...")

            episodes = get_sonarr_episodes_for_series(base_url, api_key, series_id, session)

            if episodes is None:
                # print(f"Warning: Failed to fetch episodes for series '{series_title}' (ID: {series_id}). Skipping.")
                continue # Silently skip if fetching episodes fails, reduces noise

            for episode in episodes:
                if episode.get("hasFile") and episode.get("episodeFileId", 0) > 0:
                    episode_file_id = episode["episodeFileId"]
                    season_num = episode.get("seasonNumber", 0)
                    episode_num = episode.get("episodeNumber", 0)
                    # Store essential info needed *after* file details are fetched
                    episode_info = {
                        "Series Title": series_title,
                        "Episode": f"S{season_num:02d}E{episode_num:02d}",
                        "Episode Title": episode.get("title", "N/A"),
                        "QualityProfileId": series_quality_profile_id, # Store the series' profile ID
                        "OriginalEpisodeFileId": episode_file_id # Keep for matching later if needed
                    }
                    episodes_to_process.append((episode_info, episode_file_id))

    print(f"\nPhase 1 completed. Found {len(episodes_to_process)} episodes with files across {total_series} series.")
    if not episodes_to_process:
        print("No episodes with files found to process further.")
        return []

    print(f"\nPhase 2: Fetching {len(episodes_to_process)} episode file details using up to {MAX_WORKERS} parallel workers...")

    file_details_map = {} # Dictionary to store results: episode_file_id -> details
    tasks = []
    # Prepare arguments for each task - reuse the session
    with requests.Session() as session: # Create one session to be shared by threads
        for _, episode_file_id in episodes_to_process:
            tasks.append((base_url, api_key, episode_file_id, session))

        processed_count = 0
        # Use ThreadPoolExecutor to run fetch_single_episode_file_details concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Use map to preserve order (though we store in dict anyway) or submit for more control
            future_to_id = {executor.submit(fetch_single_episode_file_details, task): task[2] for task in tasks}

            for future in concurrent.futures.as_completed(future_to_id):
                original_id = future_to_id[future]
                try:
                    # Result is (episode_file_id, details)
                    file_id, details = future.result()
                    if details: # Store only if fetch was successful
                        file_details_map[file_id] = details
                    # else: Fetch failed, error already printed by make_api_request

                except Exception as exc:
                    print(f'Warning: Episode file ID {original_id} generated an exception: {exc}')

                processed_count += 1
                if processed_count % 100 == 0 or processed_count == len(episodes_to_process):
                    print(f"  Fetched details for {processed_count}/{len(episodes_to_process)} files...")


    print(f"\nPhase 2 completed. Successfully fetched details for {len(file_details_map)} files.")

    print("\nPhase 3: Processing results, calculating scores, and adding profile names...")
    rows = []
    processed_results_count = 0
    for episode_info, episode_file_id in episodes_to_process:
        file_details = file_details_map.get(episode_file_id) # Get fetched details using ID

        if file_details:
            processed_results_count +=1
            relative_path = file_details.get("relativePath", "N/A")
            total_score = 0

            # Method 1: Try the direct 'customFormatScore' field
            total_score = file_details.get("customFormatScore", 0)

            # Method 2: Fallback to summing from 'customFormats' list
            if total_score == 0:
                custom_formats_list = file_details.get("customFormats")
                if isinstance(custom_formats_list, list):
                    try:
                        current_sum = sum(cf.get('score', 0) for cf in custom_formats_list if isinstance(cf, dict))
                        if current_sum > 0:
                            total_score = current_sum
                    except TypeError as e:
                        print(f"Warning: Type error summing scores for {episode_info['Series Title']} {episode_info['Episode']} (File ID: {episode_file_id}). Formats: {custom_formats_list}. Error: {e}")
                        total_score = 0 # Reset on error

            # Lookup Quality Profile Name using the stored series profile ID
            profile_id = episode_info.get("QualityProfileId")
            profile_name = quality_profile_map.get(profile_id, f"Unknown ID: {profile_id}" if profile_id else "N/A")

            rows.append({
                "Series Title": episode_info["Series Title"],
                "Episode": episode_info["Episode"],
                "Episode Title": episode_info["Episode Title"],
                "File": relative_path,
                "Score": total_score,
                "Quality Profile": profile_name # Add the profile name
            })
        # else: Details couldn't be fetched for this file_id, skip it.

    end_time = time.time()
    print(f"\nPhase 3 completed. Processed {processed_results_count} results.")
    print(f"Total processing time: {end_time - start_time:.2f} seconds.")

    if not rows:
        print("No episodes with processable file details found after processing.")
        return []

    # Sort by Series Title, then Season/Episode Number implied by Episode Identifier
    print("\nSorting results...")
    return sorted(rows, key=lambda r: (r["Series Title"], r["Episode"]))


# --- Main Execution: Sonarr ---
if __name__ == "__main__":
    print("\n--- Running Sonarr Score & Profile Export (Parallel Version) ---")

    if not SONARR_URL.startswith("http://") and not SONARR_URL.startswith("https://"):
        print(f"Error: Sonarr URL '{SONARR_URL}' seems invalid. Please include http:// or https://")
    elif not SONARR_API_KEY or SONARR_API_KEY == "emptyforsecurity" or SONARR_API_KEY == "mykey": # Added check for placeholder
        print(f"Error: Sonarr API Key is missing or still set to a placeholder value. Please update SONARR_API_KEY.")
    else:
        # Use a requests Session for potential keep-alive benefits
        with requests.Session() as main_session:
            quality_profile_map = get_quality_profile_map(SONARR_URL, SONARR_API_KEY, main_session)
            all_sonarr_series = get_all_sonarr_series(SONARR_URL, SONARR_API_KEY, main_session)

        if all_sonarr_series: # Check if series map is not None
            # Call the parallel processing function, passing the profile map
            sonarr_scored_list = process_sonarr_series_and_scores_parallel(all_sonarr_series, SONARR_URL, SONARR_API_KEY, quality_profile_map)

            if sonarr_scored_list:
                # Update fieldnames for CSV
                sonarr_fieldnames = ["Series Title", "Episode", "Episode Title", "File", "Score", "Quality Profile"]
                write_csv(sonarr_scored_list, SONARR_OUTPUT_CSV, sonarr_fieldnames)
            else:
                print("Processing yielded no data to write to CSV.")
        else:
            print("Could not retrieve Sonarr series list. Exiting Sonarr export.")

    print("\n--- Sonarr Score & Profile Export Finished ---")