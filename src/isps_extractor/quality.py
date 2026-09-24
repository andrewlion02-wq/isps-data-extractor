import re
from urllib.parse import urlparse


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(value):
    """Returns whether an optional email has a basic valid format."""
    if not value:
        return True
    return bool(EMAIL_PATTERN.match(str(value).strip()))


def is_valid_phone(value):
    """Returns whether an optional phone contains at least seven digits."""
    if not value:
        return True
    digits = re.sub(r"\D", "", str(value))
    return len(digits) >= 7


def is_valid_website(value):
    """Returns whether an optional website uses HTTP(S) and has a domain."""
    if not value:
        return True
    parsed_url = urlparse(str(value).strip())
    return parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)


def profile_records(records):
    """Builds quality metrics for normalized contact records."""
    records_list = list(records)
    emails = [record.get("email", "") for record in records_list]
    phones = [record.get("phone", "") for record in records_list]
    websites = [record.get("website", "") for record in records_list]

    records_with_issues = sum(
        not (
            is_valid_email(record.get("email", ""))
            and is_valid_phone(record.get("phone", ""))
            and is_valid_website(record.get("website", ""))
        )
        for record in records_list
    )

    return {
        "records_total": len(records_list),
        "providers_unique": len(
            {
                record.get("provider_name", "")
                for record in records_list
                if record.get("provider_name", "")
            }
        ),
        "emails_present": sum(bool(value) for value in emails),
        "emails_valid": sum(
            bool(value) and is_valid_email(value) for value in emails
        ),
        "phones_present": sum(bool(value) for value in phones),
        "phones_valid": sum(
            bool(value) and is_valid_phone(value) for value in phones
        ),
        "websites_present": sum(bool(value) for value in websites),
        "websites_valid": sum(
            bool(value) and is_valid_website(value) for value in websites
        ),
        "records_with_issues": records_with_issues,
    }
