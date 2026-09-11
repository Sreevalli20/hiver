#!/usr/bin/env python3
"""
Download Customer Support on Twitter dataset from Kaggle.
"""

import os
import sys
import kaggle
from pathlib import Path
import zipfile

def download_dataset():
    """Download the Customer Support on Twitter dataset."""
    
    # Create data directory
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Download dataset
    print("Downloading Customer Support on Twitter dataset from Kaggle...")
    print("Note: You may need to configure Kaggle API credentials first.")
    print("Run: kaggle datasets download -d thoughtvector/customer-support-on-twitter")
    
    try:
        kaggle.api.dataset_download_files(
            'thoughtvector/customer-support-on-twitter',
            path=str(data_dir),
            unzip=True
        )
        print(f"Dataset downloaded to {data_dir}")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("\nAlternative: Download manually from:")
        print("https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter")
        print("And extract to data/raw/")
        sys.exit(1)

if __name__ == "__main__":
    download_dataset()
