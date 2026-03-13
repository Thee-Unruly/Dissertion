import pandas as pd
import os

def explore_sample(data_path="data/emails.csv", n=5):
    """
    Reads only the first n rows of the massive Enron dataset.
    """
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return
    
    print(f"Reading first {n} rows of {data_path}...")
    try:
        df_sample = pd.read_csv(data_path, nrows=n)
        print("\n--- SAMPLE CONTENT ---")
        # Set option to see full content of columns during display
        pd.set_option('display.max_colwidth', 100)
        
        print(df_sample.info())
        print("\nHead of data:")
        print(df_sample[['file', 'message']].head())
        
        return df_sample
        
    except Exception as e:
        print(f"Error reading dataset: {e}")
        return None

if __name__ == "__main__":
    # If run in 'notebooks' folder or project root
    # For now, assuming project root based on our setup
    explore_sample()
