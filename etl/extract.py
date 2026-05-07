import os
import requests
import pandas as pd 

# -- Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "..",'data')
FILE_NAME = 'yellow_tripdata_2024-01.parquet'
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)
URL = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet'
LOC_FILE_NAME = 'taxi_zone_lookup.csv'
LOC_FILE_PATH = os.path.join(DATA_DIR, LOC_FILE_NAME)


def download_data():
    """Download the raw taxi parquet file if it doesn't already exist."""

    # Create data directory if it doesn't already exist 
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(FILE_PATH):
        print(f"File already exists at {FILE_PATH}, Skipping Download.")
    else:
        print(f"Downloading {FILE_NAME}...")
        response = requests.get(URL, stream=True)
        response.raise_for_status()

        with open(FILE_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Download complete. Saved to {FILE_PATH}")

def load_raw_data():
    """"Read the parquet file into a pandas DataFrame and print basic info."""
    print("\nLoading data into pandas...")
    df = pd.read_parquet(FILE_PATH)

    print(f"Data loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")
    return df

def load_zone_lookup():
    """Read the csv location file into a pandas DataFrame and print basic info."""
    location_df = pd.read_csv(LOC_FILE_PATH)
    return location_df

if __name__ == '__main__' :
    download_data()
    pd.set_option('display.max_columns', None)
    df = load_raw_data()