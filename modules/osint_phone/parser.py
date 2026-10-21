"""
Deep Phone Number Parser and Intelligence Extractor
Uses Google's libphonenumber engine (phonenumbers package).
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import phonenumbers
from phonenumbers import geocoder, carrier, timezone


@dataclass
class PhoneMetadata:
    raw_input: str
    is_valid: bool
    is_possible: bool
    e164: str = ""
    international: str = ""
    national: str = ""
    rfc3966: str = ""
    country_code: int = 0
    national_number: int = 0
    region_code: str = ""
    country_name: str = ""
    location: str = ""
    carrier: str = ""
    line_type: str = "Unknown"
    timezones: List[str] = field(default_factory=list)
    error: Optional[str] = None


def get_line_type_str(num_type: int) -> str:
    """Maps phonenumbers enum type to human-readable string."""
    mapping = {
        phonenumbers.PhoneNumberType.MOBILE: "Mobile / Seluler",
        phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line / Telepon Rumah",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line atau Mobile",
        phonenumbers.PhoneNumberType.TOLL_FREE: "Toll-Free / Bebas Pulsa",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
        phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
        phonenumbers.PhoneNumberType.VOIP: "VoIP (Virtual / Internet)",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
        phonenumbers.PhoneNumberType.PAGER: "Pager",
        phonenumbers.PhoneNumberType.UAN: "Universal Access Number (UAN)",
        phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail",
        phonenumbers.PhoneNumberType.UNKNOWN: "Unknown / Tidak Diketahui",
    }
    return mapping.get(num_type, "Unknown")


def parse_phone_number(raw_phone: str, default_region: str = "ID") -> PhoneMetadata:
    """
    Parses any international or national phone number and extracts rich metadata.
    Supports clean numbers with or without '+' sign.
    """
    cleaned = raw_phone.strip()
    # Normalize: if user typed e.g. "0812..." with ID region, libphonenumber handles it.
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]

    try:
        parsed = phonenumbers.parse(cleaned, default_region.upper() if default_region else None)
    except phonenumbers.NumberParseException as e:
        return PhoneMetadata(
            raw_input=raw_phone,
            is_valid=False,
            is_possible=False,
            error=str(e)
        )

    is_valid = phonenumbers.is_valid_number(parsed)
    is_possible = phonenumbers.is_possible_number(parsed)

    e164_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    intl_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    nat_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
    rfc_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.RFC3966)

    region_code = phonenumbers.region_code_for_number(parsed) or ""
    country_name = geocoder.description_for_number(parsed, "id") or geocoder.description_for_number(parsed, "en") or region_code
    carrier_name = carrier.name_for_number(parsed, "id") or carrier.name_for_number(parsed, "en") or "Unknown Carrier"
    num_type = phonenumbers.number_type(parsed)
    type_str = get_line_type_str(num_type)
    tzs = list(timezone.time_zones_for_number(parsed))

    return PhoneMetadata(
        raw_input=raw_phone,
        is_valid=is_valid,
        is_possible=is_possible,
        e164=e164_fmt,
        international=intl_fmt,
        national=nat_fmt,
        rfc3966=rfc_fmt,
        country_code=parsed.country_code,
        national_number=parsed.national_number,
        region_code=region_code,
        country_name=country_name,
        location=country_name,
        carrier=carrier_name,
        line_type=type_str,
        timezones=tzs
    )
