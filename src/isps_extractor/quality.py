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


def _record_keys(record):
    provider = str(record.get("provider_name", "")).strip().casefold()
    keys = []
    email = str(record.get("email", "")).strip().casefold()
    phone = re.sub(r"\D", "", str(record.get("phone", "")))
    if provider and email:
        keys.append(("email", provider, email))
    if provider and phone:
        keys.append(("phone", provider, phone))
    return keys


def _merge_record(target, source):
    for field_name, value in source.items():
        if field_name == "source_file":
            continue
        if not target.get(field_name) and value:
            target[field_name] = value

    sources = []
    for source_file in (target.get("source_file", ""), source.get("source_file", "")):
        for value in str(source_file).split(";"):
            if value and value not in sources:
                sources.append(value)
    if sources:
        target["source_file"] = ";".join(sources)


def deduplicate_records(records):
    """Deduplicates records by provider plus email or phone."""
    deduplicated = []
    active = []
    key_to_index = {}
    duplicates_removed = 0

    for record in records:
        current_record = dict(record)
        matching_indices = {
            key_to_index[key]
            for key in _record_keys(current_record)
            if key in key_to_index and active[key_to_index[key]]
        }

        if not matching_indices:
            deduplicated.append(current_record)
            active.append(True)
            target_index = len(deduplicated) - 1
        else:
            target_index = min(matching_indices)
            duplicates_removed += 1
            for matching_index in matching_indices:
                if matching_index == target_index:
                    continue
                _merge_record(deduplicated[target_index], deduplicated[matching_index])
                active[matching_index] = False
                duplicates_removed += 1
            _merge_record(deduplicated[target_index], current_record)

        for key in _record_keys(deduplicated[target_index]):
            key_to_index[key] = target_index

    return [record for index, record in enumerate(deduplicated) if active[index]], duplicates_removed


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


def build_quality_report(input_records, output_records, duplicates_removed):
    """Builds an analysis-ready quality report for one extraction run."""
    report = profile_records(output_records)
    report["records_input"] = len(input_records)
    report["records_output"] = len(output_records)
    report["duplicates_removed"] = duplicates_removed
    return report
