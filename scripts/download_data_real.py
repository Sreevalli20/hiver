#!/usr/bin/env python3
"""
Download Customer Support on Twitter dataset from Kaggle using kagglehub.
"""

import kagglehub
from pathlib import Path
import shutil

def download_dataset():
    """Download the Customer Support on Twitter dataset."""
    
    # Create data directory
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Download dataset using kagglehub
    print("Downloading Customer Support on Twitter dataset from Kaggle...")
    
    try:
        # Download the dataset
        path = kagglehub.dataset_download("thoughtvector/customer-support-on-twitter")
        print(f"Dataset downloaded to: {path}")
        
        # Find the CSV file in the downloaded directory
        import os
        # Check if there's a subdirectory
        subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        if subdirs:
            # Look in subdirectories
            for subdir in subdirs:
                subdir_path = os.path.join(path, subdir)
                for file in os.listdir(subdir_path):
                    if file.endswith('.csv'):
                        src_file = os.path.join(subdir_path, file)
                        dest_file = data_dir / file
                        shutil.copy(src_file, dest_file)
                        print(f"Copied {file} to {data_dir}")
        else:
            # Look in main directory
            for file in os.listdir(path):
                if file.endswith('.csv') or file.endswith('.zip'):
                    src_file = os.path.join(path, file)
                    dest_file = data_dir / file
                    
                    if file.endswith('.zip'):
                        # Extract zip file
                        import zipfile
                        with zipfile.ZipFile(src_file, 'r') as zip_ref:
                            zip_ref.extractall(data_dir)
                        print(f"Extracted {file} to {data_dir}")
                    else:
                        # Copy CSV file
                        shutil.copy(src_file, dest_file)
                        print(f"Copied {file} to {data_dir}")
        
        print(f"\nDataset successfully downloaded to {data_dir}")
        
        # List files in data/raw
        print("\nFiles in data/raw:")
        for file in data_dir.iterdir():
            print(f"  - {file.name} ({file.stat().st_size / 1024 / 1024:.2f} MB)")
        
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("\nAlternative: Download manually from:")
        print("https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter")
        print("And extract to data/raw/")
        raise

if __name__ == "__main__":
    download_dataset()
