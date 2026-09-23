from pathlib import Path

import pandas as pd


def find_csv_files(directory="."):
    """Returns the CSV files available in the working directory."""
    return sorted(
        path
        for path in Path(directory).iterdir()
        if path.is_file() and path.suffix.lower() == ".csv"
    )


def read_csv_chunks(csv_file, chunk_size):
    """Yields CSV chunks without loading the complete file into memory."""
    yield from pd.read_csv(csv_file, chunksize=chunk_size, low_memory=False)
