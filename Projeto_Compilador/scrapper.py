import requests
import os
import time
from datetime import datetime
import json

API_KEY = "52f73f0cb59745c2bfb403780e30d783"  
# Base URL for RAWG API
BASE_URL = "https://api.rawg.io/api/games?dates=2025-07-01,2025-12-31"

# ──────── OUTPUT DIRECTORY ─────────
OUTPUT_DIR = r"D:\VideoGames"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# ────────────────────────────────────

# Name of the streaming JSON file
JSON_FILENAME = os.path.join(OUTPUT_DIR, "rawg_games_stream.json")


def open_streaming_file(file_index):
    """
    Initialize a new JSON file batch with the proper structure.
    """
    filename = os.path.join(OUTPUT_DIR, f"20251_rawg_games_stream_{file_index}.json")
    template = {
        "metadata": {
            "source": "RAWG.io API",
            "fetched_at": datetime.now().isoformat(),
            "count": 0,
            "batch_index": file_index
        },
        "games": []
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    return filename


def append_games_to_stream(games_list, filename):
    """
    Append games to the given JSON file.
    """
    with open(filename, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        data['games'].extend(games_list)
        data['metadata']['count'] = len(data['games'])
        data['metadata']['fetched_at'] = datetime.now().isoformat()
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()


def get_games(page=1, page_size=20):
    """
    Fetch a page of games from RAWG.
    """
    params = {
        "key": API_KEY,
        "page": page,
        "page_size": page_size
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page}: {e}")
        return None


def main():
    if not API_KEY:
        raise RuntimeError("Set your RAWG_API_KEY environment variable first.")

    page = 1
    iteration = 0
    batch_index = 1
    current_file = open_streaming_file(batch_index)
    BATCH_SIZE = 20

    while True:
        iteration += 1
        # Rotate file every BATCH_SIZE iterations
        if iteration > 1 and (iteration - 1) % BATCH_SIZE == 0:
            batch_index += 1
            current_file = open_streaming_file(batch_index)
            print(f"Started new batch file: rawg_games_stream_{batch_index}.json")

        print(f"Fetching page {page} (iteration {iteration})...")
        data = get_games(page=page, page_size=40)
        if not data or 'results' not in data:
            print("No more data or error encountered.")
            break

        append_games_to_stream(data['results'], current_file)
        print(f"Appended {len(data['results'])} games to {os.path.basename(current_file)}.")

        if not data.get('next'):
            print("No more pages.")
            break

        page += 1
        time.sleep(0.5)

    print("Done fetching all pages.")

if __name__ == "__main__":
    main()