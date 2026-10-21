"""
OSINT Footprint Generator & Search Dork Builder
Constructs targeted search queries for discovering publicly indexed accounts,
documents, and footprints associated with a phone number.
"""
from typing import Dict, List, Tuple
from urllib.parse import quote_plus
from .parser import PhoneMetadata


def generate_osint_dorks(meta: PhoneMetadata) -> Dict[str, List[Tuple[str, str, str]]]:
    """
    Generates categorized OSINT search URLs and dorks for the given phone number.
    Returns:
        Dict[category_name -> List[(platform_name, search_url, raw_dork)]]
    """
    if not meta.is_valid and not meta.is_possible:
        return {}

    e164 = meta.e164
    national = meta.national
    digits_only = "".join(filter(str.isdigit, e164))
    nat_digits = "".join(filter(str.isdigit, national))

    # Formatted variations (clean digits and formatted)
    clean_nat = nat_digits
    if not clean_nat.startswith("0") and digits_only.startswith("62"):
        clean_nat = "0" + digits_only[2:]

    # Spaced variation (e.g. 0813 2858 0511)
    spaced_nat = ""
    if len(clean_nat) >= 10:
        spaced_nat = f"{clean_nat[:4]} {clean_nat[4:8]} {clean_nat[8:]}".strip()

    base_query = f'"{e164}" OR "{clean_nat}"'
    if spaced_nat:
        base_query += f' OR "{spaced_nat}"'

    dorks: Dict[str, List[Tuple[str, str, str]]] = {}

    # Helper URL builders
    def make_google_url(query: str) -> str:
        return f"https://www.google.com/search?q={quote_plus(query)}"

    def make_duck_url(query: str) -> str:
        return f"https://duckduckgo.com/?q={quote_plus(query)}"

    # Category: Direct Messaging & Phonebook Lookups
    dorks["Direct Messaging & Caller ID Lookups"] = [
        ("WhatsApp Direct (Cek Profil/Foto)", f"https://wa.me/{digits_only}", f"wa.me/{digits_only}"),
        ("Telegram Direct", f"https://t.me/+{digits_only}", f"t.me/+{digits_only}"),
        ("Truecaller Web Lookup", f"https://www.truecaller.com/search/id/{clean_nat}", f"truecaller.com/search/id/{clean_nat}"),
        ("Sync.me Caller Directory", f"https://sync.me/search/?number={quote_plus(e164)}", f"sync.me/search/?number={e164}")
    ]

    # Category: Global Search Engine Footprints (Paling Luas & Efektif)
    dorks["Pencarian Jejak Publik (Paling Ampuh)"] = [
        (
            "Pencarian Luas Google (Semua Website/Forum/FB)",
            make_google_url(base_query),
            base_query
        ),
        (
            "Pencarian Luas DuckDuckGo",
            make_duck_url(base_query),
            base_query
        )
    ]

    # Category: Social Media Footprints (Google Dorks)

    dorks["Social Media Footprints (Dorks)"] = [
        (
            "Instagram Accounts / Posts",
            make_google_url(f'site:instagram.com ({base_query})'),
            f'site:instagram.com ({base_query})'
        ),
        (
            "TikTok Profiles / Captions",
            make_google_url(f'site:tiktok.com ({base_query})'),
            f'site:tiktok.com ({base_query})'
        ),
        (
            "Facebook Profiles / Posts",
            make_google_url(f'site:facebook.com ({base_query})'),
            f'site:facebook.com ({base_query})'
        ),
        (
            "Twitter / X Accounts",
            make_google_url(f'site:twitter.com ({base_query})'),
            f'site:twitter.com ({base_query})'
        ),
        (
            "LinkedIn Profiles",
            make_google_url(f'site:linkedin.com ({base_query})'),
            f'site:linkedin.com ({base_query})'
        )
    ]

    # Category: Public Dumps, Pastes & Documents
    dorks["Public Pastes & Documents"] = [
        (
            "Pastebin & Text Dumps",
            make_google_url(f'site:pastebin.com OR site:justpaste.it OR site:throwbin.io ({base_query})'),
            f'site:pastebin.com OR site:justpaste.it ({base_query})'
        ),
        (
            "Leaked Files (PDF / XLSX / CSV / DOC)",
            make_google_url(f'(filetype:pdf OR filetype:xlsx OR filetype:csv OR filetype:txt) ({base_query})'),
            f'(filetype:pdf OR filetype:xlsx) ({base_query})'
        ),
        (
            "DuckDuckGo Deep Search",
            make_duck_url(f'{base_query}'),
            f'{base_query}'
        )
    ]

    # Category: Public Marketplaces & Classifieds (if region is ID or general)
    if meta.region_code == "ID":
        dorks["Indonesian Marketplaces & Classifieds"] = [
            (
                "OLX / Tokopedia / Shopee Mentions",
                make_google_url(f'(site:olx.co.id OR site:tokopedia.com OR site:shopee.co.id) ({base_query})'),
                f'(site:olx.co.id OR site:tokopedia.com) ({base_query})'
            )
        ]

    return dorks
