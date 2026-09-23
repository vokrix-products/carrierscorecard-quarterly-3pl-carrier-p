import re


ALIAS_MAP = {
    "ups": {
        "normalized": "UPS",
        "aliases": ["ups", "u.p.s.", "united parcel service", "united parcel", "ups freight"]
    },
    "fedex": {
        "normalized": "FedEx",
        "aliases": ["fedex", "federal express", "fed ex", "fedex express", "fedex ground"]
    },
    "dhl": {
        "normalized": "DHL",
        "aliases": ["dhl", "dhl express", "dhl global forwarding", "dhl supply chain"]
    },
    "usps": {
        "normalized": "USPS",
        "aliases": ["usps", "united states postal service", "u.s. postal service", "postal service"]
    }
}


def _canonical(raw: str) -> str:
    return re.sub(r"[^a-z0-9]", "", raw.strip().lower())


def normalize_carrier_name(raw: str) -> tuple:
    """Return normalized name, confidence, matched alias source.

    Confidence is 1.0 for exact alias matches. Unknown names are returned
    as the cleaned raw value with confidence 0.0.
    """
    if raw is None:
        return "", 0.0, None

    text = str(raw).strip()
    if not text:
        return "", 0.0, None

    canon = _canonical(text)

    for group in ALIAS_MAP.values():
        for alias in group["aliases"]:
            if canon == _canonical(alias):
                return group["normalized"], 1.0, text

    return text, 0.0, None
