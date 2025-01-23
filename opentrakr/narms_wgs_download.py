import os
import argparse
import requests
import pandas as pd

def download_file(target_directory, filename):
    """
    Download a file from a hardcoded URL and save it to the target directory.

    Parameters:
    - target_directory: The local directory to save the downloaded file.
    - filename: Optional. The name to save the file as. If not provided, the name will be derived from the URL.
    """
    # Hardcoded URL
    url = "https://www.fda.gov/media/93325/download?attachment"

    # Ensure the target directory exists
    os.makedirs(target_directory, exist_ok=True)

    file_path = os.path.join(target_directory, filename)

    # Download the file
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded {filename} to {file_path}")
        return file_path
    else:
        print(f"Failed to download the file. HTTP status code: {response.status_code}")
        return None

def convert_to_tab_delimited(excel_file, output_file):
    """
    Convert an Excel file to a tab-delimited text file.

    Parameters:
    - excel_file: Path to the Excel file to be converted.
    - output_file: Path to save the converted tab-delimited file.
    """
    try:
        # Load the Excel file
        df = pd.read_excel(excel_file)

        # Save as tab-delimited file
        df.to_csv(output_file, sep='\t', index=False)
        print(f"Converted {excel_file} to tab-delimited file {output_file}")
    except Exception as e:
        print(f"Error converting file: {e}")

def main():
    parser = argparse.ArgumentParser(description='Download a hardcoded file from the FDA website and convert it to a tab-delimited file.')
    parser.add_argument('-t', '--target', type=str, default='metadata_narms', help='Target directory to save the downloaded file. Defaults to the current directory.')
    parser.add_argument('-f', '--filename', type=str, default='narms_retail.xlsx', help='Optional custom filename to save the file as.')
    parser.add_argument('-o', '--output', type=str, default='narms_retail.txt', help='Optional custom filename for the tab-delimited output file.')
    args = parser.parse_args()

    # Download the file
    excel_file_path = download_file(args.target, args.filename)

    # Convert to tab-delimited if the download succeeded
    if excel_file_path:
        output_file_path = os.path.join(args.target, args.output)
        convert_to_tab_delimited(excel_file_path, output_file_path)

if __name__ == "__main__":
    main()

