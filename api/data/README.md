# Data Directory

This directory should contain the compressed datasets for the juvenile immigration analysis.

## Required Files

Place the following compressed datasets in this directory:

- `juvenile_cases_cleaned.csv.gz` - Contains detailed case information for juveniles
- `juvenile_proceedings_cleaned.csv.gz` - Contains proceedings data with decision codes
- `juvenile_reps_assigned.csv.gz` - Contains representation information for juveniles  
- `tblDecCode.csv` - Lookup table for decision code descriptions

## Note

These files are compressed CSV files that can be read directly by pandas without manual decompression, just like in the Jupyter notebook analysis.

The backend API will automatically load and process these files when endpoints are called.
