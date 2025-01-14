#!/usr/bin/env python3

import requests
import os
import re
import argparse

def download_tsv_files(base_url, target_directory):
    """
    Download all *.tsv files from a specified subdirectory on the NCBI FTP site using base Python.

    Parameters:
    - base_url: The URL of the subdirectory containing the *.tsv files.
    - target_directory: The local directory to save the downloaded files.
    """
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to access {base_url}")
        return

    # Use a regular expression to find all .tsv file links
    file_links = re.findall(r'href="([^"]+\.tsv)"', response.text)

    for href in file_links:
        download_url = f"{base_url}/{href}"
        file_response = requests.get(download_url)
        if file_response.status_code == 200:
            file_path = os.path.join(target_directory, href.split('/')[-1])
            with open(file_path, 'wb') as file:
                file.write(file_response.content)
            print(f"Downloaded {href} to {target_directory}")
        else:
            print(f"Failed to download {href}")

def download_cluster_tsv_files(base_url, target_directory):
    """
    Download all *.tsv files from the clusters subdirectory on the NCBI FTP site.

    Parameters:
    - base_url: The URL of the subdirectory containing the *.tsv files.
    - target_directory: The local directory to save the downloaded files.
    """
    response = requests.get(base_url, timeout=10)
    if response.status_code != 200:
        print(f"Failed to access {base_url}")
        return

    file_links = re.findall(r'href="((?![^"]*SNP_distances)[^"]+\.tsv)"', response.text)

    for href in file_links:
        download_url = f"{base_url}/{href}"
        file_response = requests.get(download_url)
        if file_response.status_code == 200:
            file_path = os.path.join(target_directory, href.split('/')[-1])
            with open(file_path, 'wb') as file:
                file.write(file_response.content)
            print(f"Downloaded {href} to {target_directory}")
        else:
            print(f"Failed to download {href}")

def list_available_bacteria():
    return ['Salmonella', 'Listeria', 'Campylobacter', 'Escherichia_coli_Shigella']

def main():
    bacteria_list = list_available_bacteria()
    base_url = 'https://ftp.ncbi.nlm.nih.gov/pathogen/Results'
    target_directory = '.'

    parser = argparse.ArgumentParser(description='Download TSV files from the NCBI FTP site.')
    parser.add_argument('-b', '--bacteria', type=str, help='Name of the bacteria to process. If not provided, all bacteria will be processed.')
    parser.add_argument('-l', '--list', action='store_true', help='List available bacteria and exit.')
    args = parser.parse_args()

    if args.list:
        print("Available bacteria:")
        for bacteria in bacteria_list:
            print(f"- {bacteria}")
        return

    if args.bacteria:
        if args.bacteria not in bacteria_list:
            print(f"Bacteria '{args.bacteria}' not found in the available list.")
            print("Use the -l or --list option to see all available bacteria.")
            return
        bacteria_list = [args.bacteria]

    for bacteria in bacteria_list:
        print(f"Processing {bacteria}...")
        bacteria_url = f"{base_url}/{bacteria}/latest_snps/Metadata"
        download_tsv_files(bacteria_url, target_directory)

    for bacteria in bacteria_list:
        print(f"Processing {bacteria}...")
        bacteria_url = f"{base_url}/{bacteria}/latest_snps/Clusters"
        download_cluster_tsv_files(bacteria_url, target_directory)

if __name__ == "__main__":
    main()

