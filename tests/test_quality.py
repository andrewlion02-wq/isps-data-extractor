import unittest

from isps_extractor.quality import (
    build_quality_report,
    deduplicate_records,
    is_valid_email,
    is_valid_phone,
    is_valid_website,
    profile_records,
)


class QualityTests(unittest.TestCase):
    def test_empty_contact_fields_are_valid(self):
        self.assertTrue(is_valid_email(""))
        self.assertTrue(is_valid_phone(""))
        self.assertTrue(is_valid_website(""))

    def test_validates_email_phone_and_website_formats(self):
        self.assertTrue(is_valid_email("contact@example.com"))
        self.assertFalse(is_valid_email("invalid-email"))
        self.assertTrue(is_valid_phone("+57 300 123 4567"))
        self.assertFalse(is_valid_phone("123"))
        self.assertTrue(is_valid_website("https://example.com"))
        self.assertFalse(is_valid_website("example.com"))

    def test_profiles_contact_quality_metrics(self):
        records = [
            {
                "provider_name": "ISP Uno",
                "email": "uno@example.com",
                "phone": "3001234567",
                "website": "https://ispuno.com",
            },
            {
                "provider_name": "ISP Dos",
                "email": "invalid",
                "phone": "123",
                "website": "",
            },
        ]

        profile = profile_records(records)

        self.assertEqual(profile["records_total"], 2)
        self.assertEqual(profile["providers_unique"], 2)
        self.assertEqual(profile["emails_present"], 2)
        self.assertEqual(profile["emails_valid"], 1)
        self.assertEqual(profile["phones_present"], 2)
        self.assertEqual(profile["phones_valid"], 1)
        self.assertEqual(profile["websites_present"], 1)
        self.assertEqual(profile["websites_valid"], 1)
        self.assertEqual(profile["records_with_issues"], 1)

    def test_deduplicates_by_provider_and_email_and_merges_sources(self):
        records = [
            {
                "provider_name": "ISP Uno",
                "email": "CONTACTO@ISPUNO.COM",
                "phone": "",
                "source_file": "first.csv",
            },
            {
                "provider_name": " ISP Uno ",
                "email": "contacto@ispuno.com",
                "phone": "3001234567",
                "source_file": "second.csv",
            },
        ]

        deduplicated, duplicates_removed = deduplicate_records(records)

        self.assertEqual(duplicates_removed, 1)
        self.assertEqual(len(deduplicated), 1)
        self.assertEqual(deduplicated[0]["source_file"], "first.csv;second.csv")
        self.assertEqual(deduplicated[0]["phone"], "3001234567")

    def test_keeps_records_without_contact_identifiers(self):
        records = [
            {"provider_name": "ISP Uno", "email": "", "phone": ""},
            {"provider_name": "ISP Uno", "email": "", "phone": ""},
        ]

        deduplicated, duplicates_removed = deduplicate_records(records)

        self.assertEqual(duplicates_removed, 0)
        self.assertEqual(len(deduplicated), 2)

    def test_builds_quality_report_for_analysis(self):
        input_records = [
            {
                "provider_name": "ISP Uno",
                "email": "uno@example.com",
                "phone": "3001234567",
                "website": "https://ispuno.com",
            },
            {
                "provider_name": "ISP Uno",
                "email": "uno@example.com",
                "phone": "3001234567",
                "website": "https://ispuno.com",
            },
        ]
        output_records = [input_records[0]]

        report = build_quality_report(input_records, output_records, 1)

        self.assertEqual(report["records_input"], 2)
        self.assertEqual(report["records_output"], 1)
        self.assertEqual(report["duplicates_removed"], 1)
        self.assertEqual(report["providers_unique"], 1)
        self.assertEqual(report["emails_valid"], 1)
        self.assertEqual(report["records_with_issues"], 0)


if __name__ == "__main__":
    unittest.main()
