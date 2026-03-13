import pandas as pd
import email
from email.policy import default
import os
from tqdm import tqdm

def parse_raw_message(raw_message):
    """
    Parses a raw email string into a dictionary of headers and body.
    """
    try:
        msg = email.message_from_string(raw_message, policy=default)
        
        # Extract headers
        parsed_data = {
            "Date": msg.get("Date"),
            "From": msg.get("From"),
            "To": msg.get("To"),
            "Subject": msg.get("Subject"),
            "X-From": msg.get("X-From"),
            "X-To": msg.get("X-To"),
        }
        
        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode(errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors='ignore')
            
        parsed_data["Body"] = body.strip()
        return parsed_data
    except Exception as e:
        return {"Error": str(e)}

def process_dataset(input_path="data/emails.csv", output_path="data/processed_enron.csv", chunk_size=5000, limit=10000):
    """
    Processes the large Enron CSV in chunks and saves parsed results.
    Limit is set to 10k by default for initial analysis.
    """
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    print(f"Processing dataset: {input_path} (Limit: {limit} rows)")
    
    # We'll use a list to collect dictionaries for the final dataframe
    all_parsed = []
    
    # Read in chunks to be memory efficient
    count = 0
    for chunk in pd.read_csv(input_path, chunksize=chunk_size):
        for index, row in chunk.iterrows():
            parsed = parse_raw_message(row['message'])
            parsed['file'] = row['file']
            all_parsed.append(parsed)
            count += 1
            if count >= limit:
                break
        if count >= limit:
            break
            
    df_parsed = pd.DataFrame(all_parsed)
    
    # Save to CSV
    df_parsed.to_csv(output_path, index=False)
    print(f"Successfully processed {len(df_parsed)} emails.")
    print(f"Results saved to: {output_path}")
    
    return df_parsed

if __name__ == "__main__":
    # Ensure current dir is project root
    process_dataset()
