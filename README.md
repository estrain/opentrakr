# opentrakr

## Overview
This repository contains two main scripts designed for handling bacteria-related data from the NCBI FTP site and USDA FSIS datasets. These scripts include functions for downloading, processing, and joining data files to streamline workflows related to microbiology and food safety.

---

## ncbi_tsv_download.py: NCBI Bacteria TSV Downloader

### Description
This script downloads TSV files from the NCBI FTP site for specified bacteria and organizes them into a target directory. Users can process all available bacteria or select a specific one.

### Functions

1. **`list_available_bacteria()`**
   - Lists all bacteria available for processing from the NCBI FTP site.

2. **`download_tsv_files(bacteria_url, target_directory)`**
   - Downloads TSV files from the specified bacteria metadata URL to the target directory.

3. **`download_cluster_tsv_files(bacteria_url, target_directory)`**
   - Downloads cluster TSV files for the specified bacteria to the target directory.

### Command-Line Arguments
- `-b`, `--bacteria`: Specify a bacteria name to process. Defaults to all available bacteria if not provided.
- `-l`, `--list`: List all available bacteria and exit.

### Example Usage
```bash
python ncbi_tsv_download.py.py -b Salmonella
python ncbi_tsv_download.py.py -l
```

---

## Script 2: `main()` (FSIS Data Workflow)

### Description
This script supports multiple operations for downloading, processing, merging, and joining USDA FSIS datasets. It also offers a complete workflow for automating these tasks.

### Operations

1. **`download_firefox`**
   - Downloads files using the Firefox browser and Selenium with a specified geckodriver.

2. **`download_curl`**
   - Downloads files using `curl`.

3. **`process`**
   - Processes JSON files from the output folder.

4. **`merge`**
   - Merges CSV files by type within the output folder.

5. **`join`**
   - Joins primary and secondary merged USDA FSIS datasets and writes the results to the specified output file.

6. **`complete_workflow`**
   - Runs the entire workflow, from downloading to joining data.

### Command-Line Arguments
- `operation` (required): The operation to perform. Options include:
  - `download_firefox`
  - `download_curl`
  - `process`
  - `merge`
  - `join`
  - `complete_workflow`
- `--output_file`: Output file for joined data. Defaults to `fsis_wgs.csv`.
- `--output_folder`: Folder for downloading and processing files. Defaults to `fsis_output`.
- `--download_method`: Method for downloading files. Options are `curl` (default) or `firefox`.
- `--geckodriver_path`: Path to the geckodriver executable. Defaults to `geckodriver`.

### Example Usage
```bash
python script2.py download_firefox --output_folder data --geckodriver_path /path/to/geckodriver
python script2.py process --output_folder data
python script2.py join --output_file final_output.csv
```

