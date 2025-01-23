import argparse
import pandas as pd
import os

def read_and_label_files(directory, file_pattern, label_column, label_value):
    """
    Reads files matching a pattern, adds a label column, and concatenates them into a single DataFrame.
    
    Parameters:
    - directory: Directory to search for files.
    - file_pattern: Pattern to match files (e.g., '*.metadata.tsv' or '*.all_isolates.tsv').
    - label_column: Name of the column to add as a label (e.g., 'type').
    - label_value: Function to determine the label value based on the filename.
    
    Returns:
    - A pandas DataFrame containing the concatenated data.
    """
    dfs = []  # List to hold dataframes
    for filename in os.listdir(directory):
        if filename.endswith(file_pattern):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath, sep="\t", dtype=str)
            if label_column:
                df[label_column] = label_value(filename)
            dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def main():
    parser = argparse.ArgumentParser(description="Merge and process metadata files.")
    parser.add_argument(
        "directory",
        type=str,
        help="Directory to search for input files."
    )
    parser.add_argument(
        "output_file",
        type=str,
        help="Path to save the merged output file."
    )
    args = parser.parse_args()

    directory = args.directory
    output_file = args.output_file

    # Read and label metadata files
    metadata_pattern = '.metadata.tsv'
    metadata = read_and_label_files(directory, metadata_pattern, 'type', lambda f: f.split('.')[1])

    if metadata.empty:
        print("No metadata files found. Exiting.")
        return

    # Find common columns across all metadata files
    common_columns = list(set.intersection(*(set(metadata.columns) for _ in [metadata])))
    
    # Filter each metadata dataframe to keep only common columns
    metadata = metadata[common_columns]

    # Save the merged data to a CSV file
    metadata.to_csv(output_file, index=False, sep='\t')
    print(f"Merged metadata saved to {output_file}")

if __name__ == "__main__":
    main()
