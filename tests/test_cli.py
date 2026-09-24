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

    def test_save_quality_report_creates_missing_output_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_file = Path(temporary_directory) / "new" / "quality.xlsx"

            cli.save_quality_report({"records_total": 1}, output_file)

            self.assertTrue(output_file.exists())

    def test_split_dataframe_respects_excel_row_limit(self):
        data = pd.DataFrame({"provider_name": range(5)})

        chunks = list(cli.split_dataframe(data, max_rows=3))

        self.assertEqual([len(chunk) for chunk in chunks], [3, 2])
        self.assertEqual(chunks[0]["provider_name"].tolist(), [0, 1, 2])

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
                        with patch.object(cli, "save_quality_report") as save_quality_report:
                            cli.main(
                                [
                                    "--input",
                                    "data",
                                    "--contacts-output",
                                    "contacts.xlsx",
                                    "--providers-output",
                                    "providers.xlsx",
                                    "--quality-output",
                                    "quality.xlsx",
                                ]
                            )

        find_files.assert_called_once_with("data")
        save_contacts.assert_called_once_with(records, "contacts.xlsx")
        save_providers.assert_called_once_with({"ISP Uno"}, "providers.xlsx")
        save_quality_report.assert_called_once()
        self.assertEqual(save_quality_report.call_args.args[1], "quality.xlsx")


if __name__ == "__main__":
    unittest.main()
