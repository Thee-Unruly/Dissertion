import os
import kagglehub
import shutil
import glob

def ingest_enron_dataset(target_dir="data"):
    """
    Downloads and moves the Enron Email Dataset into the project's data directory.
    """
    print("Starting dataset download for: wcukierski/enron-email-dataset")
    
    try:
        # 1. Download to kagglehub's cache
        cache_path = kagglehub.dataset_download("wcukierski/enron-email-dataset")
        print(f"Dataset downloaded/found in temporary path: {cache_path}")

        # 2. Ensure target_dir exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"Created target directory: {target_dir}")

        # 3. Move/Copy files into the target_dir
        # We look for all files in the cache_path and move them to target_dir.
        # This is useful so the script works anywhere and brings the data into the project structure.
        files_found = glob.glob(os.path.join(cache_path, "*"))
        
        for file_path in files_found:
            filename = os.path.basename(file_path)
            target_path = os.path.join(target_dir, filename)
            
            if os.path.isfile(file_path):
                print(f"Moving {filename} to {target_dir}...")
                # We use shutil.move which handles cross-device moves if necessary
                shutil.move(file_path, target_path)
                print(f"Done: {target_path}")
            elif os.path.isdir(file_path):
                # If there are subdirectories, we could handle them recursively here
                # For this dataset, we expect a single CSV
                pass
        
        return target_dir
        
    except Exception as e:
        print(f"Failed to ingest dataset: {e}")
        return None

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Use absolute path if possible or keep relative to project root
    target_data_dir = os.path.join(current_dir, "data")
    
    result_path = ingest_enron_dataset(target_data_dir)
    
    if result_path and os.path.exists(os.path.join(result_path, "emails.csv")):
        print(f"Success! Enron dataset is ready at: {result_path}")
    else:
        print("Dataset ingestion check failed or file not found in target directory.")
