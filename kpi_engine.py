from carrier_normalizer import normalize_carrier_name
from threshold_engine import (
    DEFAULT_SEGMENT,
    evaluate_threshold,
    STATUS_GREEN,
    STATUS_AMBER,
    STATUS_RED,
    STATUS_UNKNOWN,
)


KPI_DEFINITIONS = [
    {"key": "on_time_delivery_percent", "label": "On-Time Delivery %", "direction": "higher_better"},
    {"key": "on_time_pickup_percent", "label": "On-Time Pickup %", "direction": "higher_better"},
    {"key": "tender_acceptance_rate", "label": "Tender Acceptance Rate", "direction": "higher_better"},
    {"key": "claims_damage_ratio", "label": "Claims/Damage Ratio", "direction": "lower_better"},
    {"key": "invoice_accuracy", "label": "Invoice Accuracy %", "direction": "higher_better"},
    {"key": "giveback_percent", "label": "Giveback %", "direction": "higher_better"},
    {"key": "cost_variance_percent", "label": "Cost Variance %", "direction": "lower_better"},
]

FIELD_ALIASES = {
    "carrier": ["carrier", "carrier name", "carrier_name", "provider", "vendor", "3pl"],
    "on_time_delivery_percent": ["on time delivery", "on_time_delivery", "otd", "on-time delivery %", "on time delivery %"],
    "on_time_pickup_percent": ["on time pickup", "on_time_pickup", "otp", "on-time pickup %"],
    "tender_acceptance_rate": ["tender acceptance", "tender_acceptance", "tender acceptance rate", "tender accept %"],
    "claims_damage_ratio": ["claims", "claims ratio", "damage ratio", "claims_damage_ratio", "claims/damage ratio"],
    "invoice_accuracy": ["invoice accuracy", "invoice_accuracy", "invoice accuracy %", "billing accuracy"],
    "giveback_percent": ["giveback", "giveback %", "giveback_percent", "give back %"],
    "cost_variance_percent": ["cost variance", "cost_variance", "cost variance %", "cost_variance_percent"],
    "period": ["period", "quarter", "quarter period", "reporting period"],
    "segment": ["segment", "business segment", "division"],
}


def _to_float(value):
    if value is None:
        return None
    try:
        return float(str(value).replace("%", "").replace(",", "").replace("$", "").strip())
    except (TypeError, ValueError):
        return None


def _to_ratio(value, as_percent=True):
    numeric = _to_float(value)
    if numeric is None:
        return None
    if as_percent and numeric > 1.0:
        return numeric / 100.0
    return numeric


def compute_on_time_delivery_percent(on_time, total):
    """Return OTD % given delivered-on-time count and total count."""
    otd = _to_float(on_time)
    tot = _to_float(total)
    if not tot:
        return None
    return round((otd or 0.0) / tot * 100.0, 2)


def compute_claims_damage_ratio(claims, shipments):
    """Return claims/damage ratio per 100 shipments."""
    c = _to_float(claims)
    s = _to_float(shipments)
    if not s:
        return None
    return round((c or 0.0) / s * 100.0, 3)


def compute_cost_variance_percent(actual, baseline):
    """Return cost variance % as (actual - baseline) / baseline * 100."""
    a = _to_float(actual)
    b = _to_float(baseline)
    if not b:
        return None
    return round((a - b) / b * 100.0, 3)


def compute_scorecard(metrics: dict, segment: str = DEFAULT_SEGMENT) -> dict:
    """Given a dict of metric values, return status per metric plus rollup."""
    results = {}
    counts = {STATUS_GREEN: 0, STATUS_AMBER: 0, STATUS_RED: 0, STATUS_UNKNOWN: 0}

    for definition in KPI_DEFINITIONS:
        key = definition["key"]
        value = metrics.get(key)
        status, rule = evaluate_threshold(key, value, segment)
        results[key] = {
            "label": definition["label"],
            "value": value,
            "status": status,
            "threshold": rule,
        }
        counts[status] = counts.get(status, 0) + 1

    if counts[STATUS_RED] > 0:
        overall = STATUS_RED
    elif counts[STATUS_AMBER] > 0:
        overall = STATUS_AMBER
    elif counts[STATUS_GREEN] > 0:
        overall = STATUS_GREEN
    else:
        overall = STATUS_UNKNOWN

    return {
        "segment": segment,
        "metrics": results,
        "counts": counts,
        "overall_status": overall,
    }


def _find_value(record: dict, aliases: list):
    normalized_keys = {str(k).strip().lower(): k for k in record.keys()}
    for alias in aliases:
        candidate = alias.strip().lower()
        if candidate in normalized_keys:
            return record[normalized_keys[candidate]]
    return None


def compute_record_kpis(record: dict, segment: str = DEFAULT_SEGMENT) -> dict:
    """Extract and compute KPIs for a single raw record dict."""
    metrics = {}
    for key, aliases in FIELD_ALIASES.items():
        if key in ("carrier", "period", "segment"):
            continue
        metrics[key] = _find_value(record, aliases)

    carrier_raw = _find_value(record, FIELD_ALIASES["carrier"])
    normalized, confidence, matched = normalize_carrier_name(carrier_raw)

    record_segment = _find_value(record, FIELD_ALIASES["segment"]) or segment
    period = _find_value(record, FIELD_ALIASES["period"])

    scorecard = compute_scorecard(metrics, str(record_segment))

    return {
        "carrier_raw": carrier_raw,
        "carrier": normalized,
        "carrier_confidence": confidence,
        "carrier_matched_alias": matched,
        "period": period,
        "segment": str(record_segment),
        "scorecard": scorecard,
    }


def placeholder_record(record: dict, segment: str = DEFAULT_SEGMENT) -> dict:
    """Return a partial record skeleton without computing statuses."""
    carrier_raw = _find_value(record, FIELD_ALIASES["carrier"])
    normalized, confidence, matched = normalize_carrier_name(carrier_raw)
    return {
        "carrier_raw": carrier_raw,
        "carrier": normalized,
        "carrier_confidence": confidence,
        "carrier_matched_alias": matched,
        "segment": segment,
        "scorecard": None,
    }
