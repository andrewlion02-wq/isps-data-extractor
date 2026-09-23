import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from isps_extractor import cli


class CliTests(unittest.TestCase):
    def test_save_contacts_writes_normalized_excel(self):
        records = [
            {
                "provider_name": "ISP Uno",
                "contact_name": "Ana",
                "phone": "3001234567",
                "email": "ana@example.com",
                "website": "",
                "address": "",
                "source_file": "providers.csv",
            }
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_file = Path(temporary_directory) / "contacts.xlsx"
            cli.save_contacts(records, output_file)

            result = pd.read_excel(output_file)

        self.assertEqual(result.loc[0, "provider_name"], "ISP Uno")
        self.assertEqual(result.loc[0, "email"], "ana@example.com")
        self.assertEqual(result.loc[0, "source_file"], "providers.csv")

    def test_save_providers_writes_sorted_unique_names(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_file = Path(temporary_directory) / "providers.xlsx"
            providers = cli.save_providers({"ISP Dos", "ISP Uno"}, output_file)

            result = pd.read_excel(output_file)

        self.assertEqual(providers, ["ISP Dos", "ISP Uno"])
        self.assertEqual(result["Nombre_del_ISP"].tolist(), ["ISP Dos", "ISP Uno"])

    def test_main_reports_when_no_csv_files_are_found(self):
        with patch.object(cli, "find_csv_files", return_value=[]):
            with patch("builtins.print") as print_mock:
                cli.main([])

        print_mock.assert_called_once()
        self.assertIn("No encontramos", print_mock.call_args.args[0])

    def test_main_accepts_input_and_output_arguments(self):
        records = [{"provider_name": "ISP Uno"}]

        with patch.object(cli, "find_csv_files", return_value=["data/source.csv"]) as find_files:
            with patch.object(cli, "extract_contacts_from_files", return_value=records):
                with patch.object(cli, "save_contacts") as save_contacts:
                    with patch.object(cli, "save_providers") as save_providers:
                        cli.main(
                            [
                                "--input",
                                "data",
                                "--contacts-output",
                                "contacts.xlsx",
                                "--providers-output",
                                "providers.xlsx",
                            ]
                        )

        find_files.assert_called_once_with("data")
        save_contacts.assert_called_once_with(records, "contacts.xlsx")
        save_providers.assert_called_once_with({"ISP Uno"}, "providers.xlsx")


if __name__ == "__main__":
    unittest.main()
