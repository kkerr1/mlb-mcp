#!/usr/bin/env python3
"""
Script to download missing pybaseball data files.
"""

import os
import ssl
import urllib.request

import pybaseball


def download_pybaseball_data():
    """Download missing pybaseball data files."""
    # Create SSL context that doesn't verify certificates (for GitHub raw files)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Get the pybaseball installation directory
    pybaseball_dir = os.path.dirname(pybaseball.__file__)
    data_dir = os.path.join(pybaseball_dir, "data")

    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    print(f"Data directory: {data_dir}")

    # List of data files that might be missing
    data_files = ["mlb_url_team_ID.csv", "fangraphs_teams.csv", "mlbstadiums.csv"]

    base_url = "https://raw.githubusercontent.com/jldbc/pybaseball/master/pybaseball/data/"

    for filename in data_files:
        filepath = os.path.join(data_dir, filename)

        if not os.path.exists(filepath):
            try:
                url = base_url + filename
                print(f"Downloading {filename} from {url}")

                # Download with custom SSL context
                request = urllib.request.Request(url)
                with urllib.request.urlopen(request, context=ssl_context) as response:
                    with open(filepath, "wb") as f:
                        f.write(response.read())

                print(f"Successfully downloaded {filename}")
            except Exception as e:
                print(f"Failed to download {filename}: {e}")
        else:
            print(f"{filename} already exists")

    # Verify the files exist and show their sizes
    print("\nFile verification:")
    for filename in data_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"{filename}: {size} bytes")
        else:
            print(f"{filename}: MISSING")


if __name__ == "__main__":
    download_pybaseball_data()
