import argparse
from pathlib import Path

import pandas as pd

from .config import (
    CONTACTS_OUTPUT_FILE,
    EXCEL_MAX_DATA_ROWS,
    OUTPUT_FILE,
    QUALITY_OUTPUT_FILE,
)
from .input_reader import find_csv_files
from .processor import extract_contacts_from_files
from .quality import build_quality_report, deduplicate_records


def ensure_output_directory(output_file):
    """Creates the parent directory required by an output file."""
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)


def split_dataframe(dataframe, max_rows):
    """Yields dataframe slices that fit within a spreadsheet row limit."""
    for start in range(0, len(dataframe), max_rows):
        yield dataframe.iloc[start : start + max_rows]


def save_providers(providers, output_file=OUTPUT_FILE):
    """Saves the unique providers to the existing Excel output format."""
    ensure_output_directory(output_file)
    provider_list = sorted(providers)
    result = pd.DataFrame(provider_list, columns=["Nombre_del_ISP"])
    result.to_excel(output_file, index=False)
    return provider_list


def save_contacts(records, output_file=CONTACTS_OUTPUT_FILE):
    """Saves normalized provider contacts to an Excel file."""
    ensure_output_directory(output_file)
    result = pd.DataFrame(records)
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for sheet_number, chunk in enumerate(
            split_dataframe(result, EXCEL_MAX_DATA_ROWS),
            start=1,
        ):
            chunk.to_excel(
                writer,
                sheet_name=f"contacts_{sheet_number}",
                index=False,
            )
    return result


def save_quality_report(report, output_file=QUALITY_OUTPUT_FILE):
    """Saves one extraction quality summary to an Excel file."""
    ensure_output_directory(output_file)
    result = pd.DataFrame([report])
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
    parser.add_argument(
        "--quality-output",
        default=QUALITY_OUTPUT_FILE,
        help="Output Excel file for quality metrics.",
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
        input_records = extract_contacts_from_files(csv_files)

        if input_records:
            records, duplicates_removed = deduplicate_records(input_records)
            quality_report = build_quality_report(
                input_records,
                records,
                duplicates_removed,
            )
            save_contacts(records, options.contacts_output)
            providers = {record["provider_name"] for record in records}
            save_providers(providers, options.providers_output)
            save_quality_report(quality_report, options.quality_output)
            print(f"\n¡Éxito! Se encontraron {len(providers)} empresas proveedoras (ISPs) únicas.")
            print(
                "📊 Calidad: "
                f"{quality_report['records_output']} registros, "
                f"{quality_report['records_with_issues']} con problemas, "
                f"{duplicates_removed} duplicados eliminados."
            )
            print(
                "   Correos válidos: "
                f"{quality_report['emails_valid']}/{quality_report['emails_present']} | "
                "Teléfonos válidos: "
                f"{quality_report['phones_valid']}/{quality_report['phones_present']} | "
                "Webs válidas: "
                f"{quality_report['websites_valid']}/{quality_report['websites_present']}"
            )
            print(f"💾 Los contactos han sido guardados como '{options.contacts_output}'")
            print(f"💾 La lista de proveedores ha sido guardada como '{options.providers_output}'")
            print(f"💾 El reporte de calidad ha sido guardado como '{options.quality_output}'")
    except Exception as error:
        print(f"❌ Ocurrió un error al procesar el archivo: {error}")


if __name__ == "__main__":
    main()
