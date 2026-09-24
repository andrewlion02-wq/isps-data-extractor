import tempfile
import unittest
from pathlib import Path

import pandas as pd

from isps_extractor.processor import (
    extract_contacts,
    extract_contacts_from_files,
    extract_unique_providers,
    find_provider_column,
    iter_contacts,
    iter_contacts_from_files,
)


class ProcessorTests(unittest.TestCase):
    def test_find_provider_column_uses_supported_names(self):
        self.assertEqual(find_provider_column(["Empresa"]), "Empresa")
        self.assertIsNone(find_provider_column(["unknown"]))

    def test_find_provider_column_accepts_normalized_column_variants(self):
        self.assertEqual(find_provider_column(["razon_social"]), "razon_social")

    def test_extract_contacts_accepts_normalized_contact_column_variants(self):
        data = pd.DataFrame(
            {
                "razon_social": ["ISP Uno"],
                "correo-electronico": ["uno@example.com"],
            }
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "normalized-columns.csv"
            data.to_csv(csv_path, index=False)

            records = extract_contacts(csv_path)

        self.assertEqual(records[0]["provider_name"], "ISP Uno")
        self.assertEqual(records[0]["email"], "uno@example.com")

    def test_extract_unique_providers_cleans_and_deduplicates_values(self):
        data = pd.DataFrame(
            {
                "Empresa": [" ISP Uno ", "ISP Uno", None, "ISP Dos ", ""]
            }
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "providers.csv"
            data.to_csv(csv_path, index=False)

            providers = extract_unique_providers(csv_path)

        self.assertEqual(providers, {"ISP Uno", "ISP Dos"})

    def test_extract_contacts_returns_normalized_provider_and_contact_fields(self):
        data = pd.DataFrame(
            {
                "Razon Social": [" ISP Uno "],
                "Correo": [" contacto@ispuno.co "],
                "Telefono": [" 300 123 4567 "],
            }
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "contacts.csv"
            data.to_csv(csv_path, index=False)

            records = extract_contacts(csv_path)

        self.assertEqual(
            records,
            [
                {
                    "provider_name": "ISP Uno",
                    "contact_name": "",
                    "phone": "300 123 4567",
                    "email": "contacto@ispuno.co",
                    "website": "",
                    "address": "",
                    "source_file": "contacts.csv",
                }
            ],
        )

    def test_extract_contacts_ignores_rows_without_provider_name(self):
        data = pd.DataFrame(
            {
                "Empresa": ["ISP Uno", "   "],
                "Email": ["uno@example.com", "sin-proveedor@example.com"],
            }
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "contacts.csv"
            data.to_csv(csv_path, index=False)

            records = extract_contacts(csv_path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["provider_name"], "ISP Uno")

    def test_extract_contacts_from_files_processes_every_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            first_csv = Path(temporary_directory) / "first.csv"
            second_csv = Path(temporary_directory) / "second.csv"
            pd.DataFrame({"Empresa": ["ISP Uno"]}).to_csv(first_csv, index=False)
            pd.DataFrame({"Empresa": ["ISP Dos"]}).to_csv(second_csv, index=False)

            records = extract_contacts_from_files([first_csv, second_csv])

        self.assertEqual(
            [(record["provider_name"], record["source_file"]) for record in records],
            [("ISP Uno", "first.csv"), ("ISP Dos", "second.csv")],
        )

    def test_iter_contacts_yields_records_progressively(self):
        data = pd.DataFrame({"Empresa": ["ISP Uno", "ISP Dos"]})

        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "providers.csv"
            data.to_csv(csv_path, index=False)

            records_iterator = iter_contacts(csv_path)

            self.assertTrue(hasattr(records_iterator, "__next__"))
            self.assertEqual(next(records_iterator)["provider_name"], "ISP Uno")
            self.assertEqual(next(records_iterator)["provider_name"], "ISP Dos")

    def test_iter_contacts_from_files_preserves_all_sources(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            first_csv = Path(temporary_directory) / "first.csv"
            second_csv = Path(temporary_directory) / "second.csv"
            pd.DataFrame({"Empresa": ["ISP Uno"]}).to_csv(first_csv, index=False)
            pd.DataFrame({"Empresa": ["ISP Dos"]}).to_csv(second_csv, index=False)

            records = list(iter_contacts_from_files([first_csv, second_csv]))

        self.assertEqual(
            [record["source_file"] for record in records],
            ["first.csv", "second.csv"],
        )


if __name__ == "__main__":
    unittest.main()
