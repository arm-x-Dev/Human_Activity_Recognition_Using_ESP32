import os
import pandas as pd

def load_and_preprocess_csi(file_path):
    """
    Loads a CSI CSV file and processes it by:
    1. Detecting packet boundaries when SubCarrier_index drops or resets.
    2. Assigning a unique sequential packet_id.
    3. Pivoting the dataframe so packet_id is the index and SubCarrier_index (0-127) are the columns.
    """
    print(f"Loading {file_path}...")
    df = pd.read_csv(file_path)
    
    # Ensure columns exist
    if 'SubCarrier_index' not in df.columns or 'amplitude' not in df.columns:
        raise ValueError(f"Required columns not found in {file_path}")
        
    # Detect packet boundaries by tracking when SubCarrier_index resets/drops
    # (i.e., current index is less than the previous index)
    is_new_packet = df['SubCarrier_index'] < df['SubCarrier_index'].shift(1)
    # The first row is always the start of the first packet
    is_new_packet.iloc[0] = True
    
    # Assign sequential packet IDs
    df['packet_id'] = is_new_packet.cumsum()
    
    print(f"  Detected {df['packet_id'].nunique()} packets in {file_path}.")
    
    # Pivot so packet_id is the row index, SubCarrier_index (0 to 127) is the columns
    pivoted = df.pivot(index='packet_id', columns='SubCarrier_index', values='amplitude')
    
    # Reindex to ensure columns 0 to 127 are present, filling any missing subcarriers with 0
    pivoted = pivoted.reindex(columns=range(128), fill_value=0.0)
    
    # Fill any individual NaN cell values with 0.0
    pivoted = pivoted.fillna(0.0)
    
    return pivoted

def main():
    # File paths and corresponding labels
    datasets = {
        'stillroom.csv': 0,
        'movingroom.csv': 1,
        'jumpingroom.csv': 2
    }
    
    pivoted_dfs = {}
    
    # 1. Load and pivot each dataframe
    for filename, label in datasets.items():
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Expected file {filename} not found in the workspace directory.")
        pivoted_dfs[filename] = load_and_preprocess_csi(filename)
        
    # 4. Drop columns that are entirely 0 across all packets
    # First, temporarily combine them to find columns that are 0 everywhere
    combined_raw = pd.concat(pivoted_dfs.values(), axis=0)
    zero_cols = combined_raw.columns[(combined_raw == 0).all(axis=0)].tolist()
    
    print(f"\nDetecting guard bands/null subcarriers entirely filled with 0 across all datasets...")
    print(f"Dropped {len(zero_cols)} columns: {zero_cols}")
    
    # Drop from each pivoted dataframe
    for filename in pivoted_dfs:
        pivoted_dfs[filename] = pivoted_dfs[filename].drop(columns=zero_cols)
        
    # 5. Append label to each pivoted matrix
    for filename, label in datasets.items():
        pivoted_dfs[filename]['label'] = label
        
    # 6. Concatenate all three datasets together
    final_df = pd.concat(pivoted_dfs.values(), axis=0, ignore_index=True)
    
    # 7. Print shape and count per label
    print("\n--- Final Matrix Verification ---")
    print(f"Combined Matrix Shape: {final_df.shape}")
    print("\nPacket count per activity label:")
    label_mapping = {0: "Still Room", 1: "Moving Room", 2: "Jumping Room"}
    counts = final_df['label'].value_counts().rename(index=label_mapping)
    print(counts)
    
    # 8. Save combined matrix to processed_csi_data.csv
    output_path = 'processed_csi_data.csv'
    final_df.to_csv(output_path, index=False)
    print(f"\nSuccessfully saved preprocessed combined matrix to '{output_path}'.")

if __name__ == '__main__':
    main()
