from pathlib import Path
import re
import unicodedata

import pandas as pd

from .config import CHUNK_SIZE, COLUMN_ALIASES, POSSIBLE_COLUMNS
from .input_reader import read_csv_chunks


def normalize_column_name(column):
    """Returns a comparable form of a source column name."""
    normalized = unicodedata.normalize("NFKD", str(column))
    normalized = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", normalized.lower())
    return normalized.strip("_")


def find_column(columns, field_name):
    """Returns the first configured source column for a normalized field."""
    normalized_columns = {
        normalize_column_name(column): column for column in columns
    }
    for column in COLUMN_ALIASES[field_name]:
        normalized_column = normalize_column_name(column)
        if normalized_column in normalized_columns:
            return normalized_columns[normalized_column]
    return None


def find_provider_column(columns):
    """Returns the first supported provider column, or None if none exists."""
    return find_column(columns, "provider_name")


def clean_value(value):
    """Converts missing values to empty strings and strips text values."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def extract_unique_providers(csv_file):
    """Reads the CSV in chunks and returns unique, cleaned provider names."""
    providers = set()
    provider_column = None

    for chunk in read_csv_chunks(csv_file, CHUNK_SIZE):
        if provider_column is None:
            provider_column = find_provider_column(chunk.columns)

            if provider_column:
                print(f"🎯 Columna identificada: '{provider_column}'")
            else:
                print("\n❌ No se encontró ninguna columna conocida de nombres.")
                print(f"Las columnas disponibles en tu archivo son: {list(chunk.columns)}")
                break

        providers.update(
            value
            for value in chunk[provider_column].map(clean_value).unique()
            if value
        )

    return providers


def extract_contacts(csv_file):
    """Extracts normalized provider and contact records from a CSV in chunks."""
    records = []
    provider_column = None
    field_columns = {}
    source_file = Path(csv_file).name

    for chunk in read_csv_chunks(csv_file, CHUNK_SIZE):
        if provider_column is None:
            provider_column = find_provider_column(chunk.columns)
            if provider_column is None:
                return records

            field_columns = {
                field_name: find_column(chunk.columns, field_name)
                for field_name in COLUMN_ALIASES
            }

        for _, row in chunk.iterrows():
            provider_name = clean_value(row[provider_column])
            if not provider_name:
                continue

            record = {
                field_name: clean_value(row[column]) if column else ""
                for field_name, column in field_columns.items()
            }
            record["source_file"] = source_file
            records.append(record)

    return records


def extract_contacts_from_files(csv_files):
    """Extracts normalized contacts from every CSV in the provided collection."""
    records = []
    for csv_file in csv_files:
        records.extend(extract_contacts(csv_file))
    return records
