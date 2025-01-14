import os
import time
import json
import pandas as pd
import argparse
import subprocess
import glob
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Shared list of file names to download
file_names = [
    "raw_poultry_sampling_data_fy2024.zip",
    "raw_poultry_sampling_data_fy2023.zip",
    "raw_poultry_sampling_data_fy2022.zip",
    "raw_poultry_sampling_data_fy2021.zip",
    "raw_poultry_sampling_data_fy2020.zip",
    "raw_poultry_sampling_data_fy2019.zip",
    "raw_poultry_sampling_data_fy2018.zip",
    "raw_poultry_sampling_data_fy2017.zip",
    "raw_poultry_sampling_data_fy2016.zip",
    "raw_poultry_sampling_data_fy2015.zip",
    "raw_poultry_sampling_data_fy2014.zip",
]

# Function to download files using Firefox
def download_files_firefox(output_folder, geckodriver_path=None):
    base_url = "https://www.fsis.usda.gov/sites/default/files/media_file/documents/"
    os.makedirs(output_folder, exist_ok=True)

    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", os.path.abspath(output_folder))
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip,application/octet-stream")
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.add_argument("--headless")

    service = Service(executable_path=geckodriver_path) if geckodriver_path else Service()

    driver = None
    try:
        driver = webdriver.Firefox(service=service, options=options)

        for file_name in file_names:
            file_url = f"{base_url}{file_name}"
            print(f"Downloading {file_url} to {os.path.abspath(output_folder)}")
            try:
                driver.set_page_load_timeout(10)
                driver.get(file_url)
            except Exception as e:
                print(f"Page load timed out for {file_name}: {e}")

            file_path = os.path.join(output_folder, file_name)
            timeout = 10
            start_time = time.time()

            while not os.path.exists(file_path):
                if time.time() - start_time > timeout:
                    print(f"Download did not complete for {file_name} within the expected time.")
                    break
                time.sleep(1)

            if os.path.exists(file_path):
                print(f"{file_name} downloaded successfully.")
                subprocess.run(["unzip", "-o", file_path, "-d", output_folder])
            else:
                print(f"{file_name} failed to download.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()
        print("WebDriver session closed.")



# Function to download files using curl
def download_files_curl(output_folder):
    base_url = "https://www.fsis.usda.gov/sites/default/files/media_file/documents/"
    os.makedirs(output_folder, exist_ok=True)

    for file_name in file_names:
        file_url = f"{base_url}{file_name}"
        output_path = os.path.join(output_folder, file_name)
        print(f"Downloading {file_url} to {output_path}")
        try:
            subprocess.run(["curl", "-o", output_path, file_url], check=True)
            print(f"{file_name} downloaded successfully.")
            # Unzip the file
            subprocess.run(["unzip", "-o", output_path, "-d", output_folder])
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {file_name}: {e}")

def process_json_files(folder_path):
    if not os.path.exists(folder_path):
        print(f"Directory does not exist: {folder_path}")
        return

    tables_per_file = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing JSON file: {file_path}")
            with open(file_path, "r") as file:
                data = json.load(file)
                extracted_tables = extract_tables_from_list(data)
                if not extracted_tables:
                    print(f"No tables extracted from {file_name}.")
                else:
                    print(f"Extracted tables from {file_name}: {list(extracted_tables.keys())}")
                tables_per_file[file_name] = extracted_tables

    # Process the extracted tables for primary and secondary CSV files
    if tables_per_file:
        print("Processing primary and secondary tables...")
        process_primary_and_secondary_tables_per_file(tables_per_file, folder_path)




def extract_tables_from_list(json_data):
    tables = {}
    if isinstance(json_data, list):
        for i, item in enumerate(json_data):
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, list):
                        print(f"Extracting DataFrame for list_item_{i}_{key}.")
                        tables[f"list_item_{i}_{key}"] = pd.DataFrame(value)
                    elif isinstance(value, dict):
                        print(f"Normalizing JSON for list_item_{i}_{key}.")
                        tables[f"list_item_{i}_{key}"] = pd.json_normalize(value)
    else:
        print("JSON data is not a list; no tables extracted.")
    return tables

def process_primary_and_secondary_tables_per_file(tables_per_file, output_folder):
    os.makedirs(output_folder, exist_ok=True)  # Ensure the output folder exists

    for file_name, tables in tables_per_file.items():
        print(f"Processing tables for {file_name}: {list(tables.keys())}")
        data_table = tables.get("list_item_0_data", None)
        primary_table, secondary_table = None, None

        # Generate a base file name without JSON extension for CSV outputs
        base_file_name = os.path.splitext(file_name)[0]

        if data_table is not None:
            print(f"Data table found for {file_name}. Columns: {data_table.columns}")
            if "primary_table_data" in data_table.columns:
                try:
                    primary_table = pd.DataFrame(data_table["primary_table_data"].iloc[0])
                    primary_csv_path = os.path.join(output_folder, f"{base_file_name}_primary_table.csv")
                    primary_table.to_csv(primary_csv_path, index=False)
                    print(f"Primary table written to {primary_csv_path}.")
                except Exception as e:
                    print(f"Error processing primary_table_data for {file_name}: {e}")

            if "secondary_table_data" in data_table.columns:
                try:
                    secondary_table = pd.DataFrame(data_table["secondary_table_data"].iloc[0])
                    secondary_csv_path = os.path.join(output_folder, f"{base_file_name}_secondary_table.csv")
                    secondary_table.to_csv(secondary_csv_path, index=False)
                    print(f"Secondary table written to {secondary_csv_path}.")
                except Exception as e:
                    print(f"Error processing secondary_table_data for {file_name}: {e}")
        else:
            print(f"No data table found for {file_name}.")


# Function to merge primary and secondary CSV files
def merge_csv_files_by_type(input_directory):
    for file_type in ["primary", "secondary"]:
        pattern = f"*{file_type}*.csv"
        output_filename = f"merged_usda_fsis_data_{file_type}.csv"

        file_list = glob.glob(os.path.join(input_directory, pattern))

        if not file_list:
            print(f"No CSV files matching the pattern found: {pattern}")
            continue

        print(f"Found {len(file_list)} files matching the pattern for {file_type}. Merging...")

        merged_data = pd.DataFrame()

        for file in file_list:
            data = pd.read_csv(file)
            data["source_file"] = os.path.basename(file)

            if merged_data.empty:
                merged_data = data
            else:
                if list(merged_data.columns) != list(data.columns):
                    print(f"Column headers do not match for file: {file}. Skipping this file.")
                    continue

                merged_data = pd.concat([merged_data, data], ignore_index=True)

        output_file = os.path.join(input_directory, output_filename)
        merged_data.to_csv(output_file, index=False)

        print(f"{file_type.capitalize()} files merged successfully! Merged file saved as {output_file}.")

# Function to join primary and secondary CSV files
import os

def join_primary_secondary(primary_file, secondary_file, output_folder, output_file):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Construct the full path for the output file
    output_file = os.path.join(output_folder, output_file)

    pri_df = pd.read_csv(primary_file)
    sec_df = pd.read_csv(secondary_file)

    # Remove duplicate form_ids in primary file
    pri_df = pri_df[~pri_df.duplicated(subset="form_id")]

    # Extract year and month from collection_date
    pri_df["collection_date"] = pd.to_datetime(pri_df["collection_date"], errors="coerce")
    pri_df["year"] = pri_df["collection_date"].dt.year
    pri_df["month"] = pri_df["collection_date"].dt.month

    # Simplify secondary data
    sec_df = sec_df[
        [
            "form_id",
            "salmonella_bio_project_number",
            "campylobacter_bio_project_number",
            "salmonella_bio_sample_accession_number",
            "campylobacter_bio_sample_accession_number",
            "salmonella_sra_accession_number",
            "campylobacter_sra_accession_number",
        ]
    ]

    sec_df["bio_project_number"] = sec_df[
        ["salmonella_bio_project_number", "campylobacter_bio_project_number"]
    ].bfill(axis=1).iloc[:, 0]
    sec_df["bio_sample_number"] = sec_df[
        ["salmonella_bio_sample_accession_number", "campylobacter_bio_sample_accession_number"]
    ].bfill(axis=1).iloc[:, 0]
    sec_df["sra_accession_number"] = sec_df[
        ["salmonella_sra_accession_number", "campylobacter_sra_accession_number"]
    ].bfill(axis=1).iloc[:, 0]

    sec_df = sec_df.drop(
        columns=[
            "salmonella_bio_project_number",
            "campylobacter_bio_project_number",
            "salmonella_bio_sample_accession_number",
            "campylobacter_bio_sample_accession_number",
            "salmonella_sra_accession_number",
            "campylobacter_sra_accession_number",
        ]
    )

    # Merge datasets using an inner join to keep only form_ids present in both files
    final_df = pd.merge(pri_df, sec_df, on="form_id", how="inner")

    # Save result to output file in the specified output folder
    final_df.to_csv(output_file, index=False)
    print(f"Joined data saved to {output_file}")



# Function to run the complete workflow
def complete_workflow(download_method, output_folder, joined_file, geckodriver_path):
    if download_method == "firefox":
        download_files_firefox(output_folder, geckodriver_path)
    else:
        download_files_curl(output_folder)

    process_json_files(output_folder)
    merge_csv_files_by_type(output_folder)

    primary_file = os.path.join(output_folder, "merged_usda_fsis_data_primary.csv")
    secondary_file = os.path.join(output_folder, "merged_usda_fsis_data_secondary.csv")

    join_primary_secondary(primary_file, secondary_file, output_folder, joined_file)

# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download, process, merge, join FSIS data, or run the complete workflow."
    )
    parser.add_argument(
        "operation",
        choices=[
            "download_firefox",
            "download_curl",
            "process",
            "merge",
            "join",
            "complete_workflow",
        ],
        help="Operation to perform: 'download_firefox', 'download_curl', 'process', 'merge', 'join', or 'complete_workflow'.",
    )
    parser.add_argument("--output_file", default="fsis_wgs.csv", help="Output file for joined data.")
    parser.add_argument(
        "--output_folder", default="fsis_output", help="Folder for downloading and processing files."
    )
    parser.add_argument(
        "--download_method",
        choices=["curl", "firefox"],
        default="curl",
        help="Method to use for downloading files (default: curl).",
    )
    parser.add_argument("--geckodriver_path", default="geckodriver", help="Path to the geckodriver executable.")

    args = parser.parse_args()

    if args.operation == "download_firefox":
        download_files_firefox(args.output_folder, args.geckodriver_path)
    elif args.operation == "download_curl":
        download_files_curl(args.output_folder)
    elif args.operation == "process":
        process_json_files(args.output_folder)
    elif args.operation == "merge":
        merge_csv_files_by_type(args.output_folder)
    elif args.operation == "join":
        primary_file = os.path.join(args.output_folder, "merged_usda_fsis_data_primary.csv")
        secondary_file = os.path.join(args.output_folder, "merged_usda_fsis_data_secondary.csv")
        join_primary_secondary(primary_file, secondary_file, args.output_folder, args.output_file)
    elif args.operation == "complete_workflow":
        complete_workflow(args.download_method, args.output_folder, args.output_file, args.geckodriver_path)