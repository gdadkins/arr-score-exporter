import requests
import csv
import json
import time
import concurrent.futures # Import for threading

# ─── CONFIG ─────────────────────────────────────────────────────────────────
API_KEY    = "YOUR_APP_API_KEY_HERE"  # Replace with your actual Radarr API Key
RADARR_URL = "http://127.0.0.1:7878" # Your Radarr host:port
OUTPUT_CSV = "radarr_custom_scores.csv"
# --- Performance Tuning ---
# Number of parallel workers to fetch file details. Adjust based on your system & Radarr's responsiveness.
# Start lower (e.g., 5-10) and increase if your system handles it well. Too high might overload Radarr.
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
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        print(f"Error: Timeout connecting to {url}")
    except requests.exceptions.HTTPError as e:
        # Don't print every 404 if just checking optional data
        if e.response.status_code != 404:
            print(f"Error: HTTP Error {e.response.status_code} for {url}")
            # print(f"Response: {e.response.text}") # Uncomment for detailed API errors
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


# --- Radarr Specific Functions ---

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

def get_all_movies(base_url, api_key, session):
    """Fetches all movies from Radarr."""
    print(f"Fetching all movies from Radarr at {base_url}...")
    endpoint = "/api/v3/movie"
    movies_data = make_api_request(base_url, api_key, endpoint, session=session)
    if movies_data is not None:
        print(f"Successfully fetched {len(movies_data)} movies.")
        return movies_data
    else:
        print("Failed to fetch movies.")
        return None

# --- Function to fetch details for ONE file (will be run in threads) ---
def fetch_single_movie_file_details(args):
    """Fetches details for a single movie file ID. Designed for ThreadPoolExecutor."""
    base_url, api_key, movie_file_id, session = args
    endpoint = f"/api/v3/movieFile/{movie_file_id}"
    # Use the session for potentially faster connection reuse within threads
    details = make_api_request(base_url, api_key, endpoint, session=session)
    return movie_file_id, details # Return ID too, to match results later


# --- Main Processing Function (Parallel Version) ---
def process_movies_and_scores_parallel(movies, base_url, api_key, quality_profile_map):
    """Processes movies, fetches file details in parallel, extracts scores and profile, returns sorted list."""
    if not movies:
        print("No movie data to process.")
        return []

    start_time = time.time()
    files_to_process = [] # List to hold (movie_info, movie_file_id) tuples

    print("Phase 1: Identifying movies with files and extracting info...")
    for movie in movies:
        movie_file_summary = movie.get("movieFile")
        if movie.get("hasFile") and movie_file_summary:
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
            #    print(f"Warning: Movie '{movie.get('title', 'N/A')}' has file but no movieFile ID found in summary. Skipping.")

    total_movies = len(movies)
    print(f"Phase 1 completed. Found {len(files_to_process)} movies with file IDs out of {total_movies} total movies.")
    if not files_to_process:
        print("No movies with processable files found.")
        return []

    print(f"\nPhase 2: Fetching {len(files_to_process)} movie file details using up to {MAX_WORKERS} parallel workers...")

    file_details_map = {} # Dictionary to store results: movie_file_id -> details
    tasks = []
    # Prepare arguments for each task - reuse a session
    with requests.Session() as session: # Create one session to be shared by threads
        for _, movie_file_id in files_to_process:
            tasks.append((base_url, api_key, movie_file_id, session))

        processed_count = 0
        # Use ThreadPoolExecutor to run fetch_single_movie_file_details concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_id = {executor.submit(fetch_single_movie_file_details, task): task[2] for task in tasks}

            for future in concurrent.futures.as_completed(future_to_id):
                original_id = future_to_id[future]
                try:
                    # Result is (movie_file_id, details)
                    file_id, details = future.result()
                    if details: # Store only if fetch was successful
                        file_details_map[file_id] = details
                    # else: Fetch failed, error already printed by make_api_request

                except Exception as exc:
                    print(f'Warning: Movie file ID {original_id} generated an exception: {exc}')

                processed_count += 1
                if processed_count % 50 == 0 or processed_count == len(files_to_process):
                    print(f"  Fetched details for {processed_count}/{len(files_to_process)} files...")

    print(f"\nPhase 2 completed. Successfully fetched details for {len(file_details_map)} files.")

    print("\nPhase 3: Processing results, calculating scores, and adding profile names...")
    rows = []
    processed_results_count = 0
    for movie_info, movie_file_id in files_to_process:
        file_details = file_details_map.get(movie_file_id) # Get fetched details using ID

        if file_details:
            processed_results_count += 1
            total_score = 0 # Default score
            custom_formats_list = None # Store for calculation

            # First, try the direct 'customFormatScore' field in the detailed response
            total_score = file_details.get("customFormatScore", 0)

            # If score is still 0 or field missing, try summing from the 'customFormats' list
            if total_score == 0:
                custom_formats_list = file_details.get("customFormats", [])
                if custom_formats_list: # Check if it's not None or empty
                    try:
                        # Ensure cf is a dictionary and has 'score' before summing
                        current_sum = sum(cf.get('score', 0) for cf in custom_formats_list if isinstance(cf, dict))
                        if current_sum > 0:
                            total_score = current_sum
                    except TypeError as e:
                        print(f"Warning: Error summing scores for '{movie_info['Title']}' (File ID: {movie_file_id}). Formats list: {custom_formats_list}. Error: {e}")
                        total_score = 0 # Reset score on error

            # Lookup Quality Profile Name
            profile_id = movie_info.get("QualityProfileId")
            profile_name = quality_profile_map.get(profile_id, f"Unknown ID: {profile_id}" if profile_id else "N/A")

            rows.append({
                "Title": movie_info["Title"],
                "File": movie_info["File"], # Use path from summary info collected earlier
                "Score": total_score,
                "Quality Profile": profile_name # Add the profile name
            })
        # else: Details couldn't be fetched for this file_id, skip it.

    end_time = time.time()
    print(f"\nPhase 3 completed. Processed {processed_results_count} results.")
    print(f"Total processing time: {end_time - start_time:.2f} seconds.")

    if not rows:
        print("No movies with processable file details found after processing.")
        return []

    # Sort by Score (descending)
    print("\nSorting results...")
    return sorted(rows, key=lambda r: r["Score"], reverse=True)


# --- Main Execution: Radarr ---
if __name__ == "__main__":
    print("\n--- Running Radarr Score & Profile Export (Parallel Version) ---")

    if not RADARR_URL.startswith("http://") and not RADARR_URL.startswith("https://"):
        print(f"Error: Radarr URL '{RADARR_URL}' seems invalid. Please include http:// or https://")
    elif not API_KEY or API_KEY == "emptyforsecurity" or API_KEY == "mykey": # Added check for placeholder
        print(f"Error: Radarr API Key is missing or still set to a placeholder value. Please update API_KEY.")
    else:
        # Use a requests Session for potential keep-alive benefits
        with requests.Session() as main_session:
            quality_profile_map = get_quality_profile_map(RADARR_URL, API_KEY, main_session)
            all_movies = get_all_movies(RADARR_URL, API_KEY, main_session)

        if all_movies:
            # Call the parallel processing function, passing the profile map
            scored_list = process_movies_and_scores_parallel(all_movies, RADARR_URL, API_KEY, quality_profile_map)

            if scored_list:
                # Update fieldnames for CSV
                radarr_fieldnames = ["Title", "File", "Score", "Quality Profile"]
                write_csv(scored_list, OUTPUT_CSV, radarr_fieldnames)
            else:
                print("Processing yielded no data to write to CSV.")
        else:
            print("Could not retrieve Radarr movie list. Exiting Radarr export.")

    print("\n--- Radarr Score & Profile Export Finished ---")