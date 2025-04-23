#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description="Run the Apply Here application with progress tracking")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the server on")
    parser.add_argument("--address", type=str, default="0.0.0.0", help="Address to bind the server to")
    args = parser.parse_args()
    
    print("Starting Apply Here application...")
    
    # Display a progress bar for startup
    with tqdm(total=100, desc="Initializing", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        # Update progress bar in chunks
        for i in range(4):
            pbar.update(25)
    
    # Launch the Streamlit application with the specified server settings
    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", str(args.port),
        "--server.address", str(args.address),
        "--server.headless", "true"
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    subprocess.call(cmd)

if __name__ == "__main__":
    main() 