import argparse

import pandas as pd

from .config import CONTACTS_OUTPUT_FILE, OUTPUT_FILE
from .input_reader import find_csv_files
from .processor import extract_contacts_from_files


def save_providers(providers, output_file=OUTPUT_FILE):
    """Saves the unique providers to the existing Excel output format."""
    provider_list = sorted(providers)
    result = pd.DataFrame(provider_list, columns=["Nombre_del_ISP"])
    result.to_excel(output_file, index=False)
    return provider_list


def save_contacts(records, output_file=CONTACTS_OUTPUT_FILE):
    """Saves normalized provider contacts to an Excel file."""
    result = pd.DataFrame(records)
    result.to_excel(output_file, index=False)
    return result


def build_parser():
    """Builds the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Extract and normalize ISP provider contacts from CSV files."
    )
    parser.add_argument(
        "--input",
        default=".",
        help="Directory containing the input CSV files.",
    )
    parser.add_argument(
        "--contacts-output",
        default=CONTACTS_OUTPUT_FILE,
        help="Output Excel file for normalized contacts.",
    )
    parser.add_argument(
        "--providers-output",
        default=OUTPUT_FILE,
        help="Output Excel file for unique providers.",
    )
    return parser


def main(arguments=None):
    """Coordinates input discovery, processing, and output."""
    options = build_parser().parse_args(arguments)
    csv_files = find_csv_files(options.input)

    if not csv_files:
        print("❌ No encontramos ningún archivo CSV en esta carpeta. Asegúrate de que el archivo esté aquí.")
        return

    print(f"📂 Archivos detectados: {len(csv_files)}")
    print("⏳ Leyendo el archivo por bloques para cuidar la RAM de tu Mac...")

    try:
        records = extract_contacts_from_files(csv_files)

        if records:
            save_contacts(records, options.contacts_output)
            providers = {record["provider_name"] for record in records}
            save_providers(providers, options.providers_output)
            print(f"\n¡Éxito! Se encontraron {len(providers)} empresas proveedoras (ISPs) únicas.")
            print(f"💾 Los contactos han sido guardados como '{options.contacts_output}'")
            print(f"💾 La lista de proveedores ha sido guardada como '{options.providers_output}'")
    except Exception as error:
        print(f"❌ Ocurrió un error al procesar el archivo: {error}")


if __name__ == "__main__":
    main()
