SEGMENT_PRESETS = {
    "retail": {
        "on_time_delivery_percent": {"green_min": 95.0, "amber_min": 90.0},
        "on_time_pickup_percent": {"green_min": 95.0, "amber_min": 90.0},
        "tender_acceptance_rate": {"green_min": 95.0, "amber_min": 85.0},
        "claims_damage_ratio": {"green_max": 0.5, "amber_max": 1.0},
        "invoice_accuracy": {"green_min": 95.0, "amber_min": 90.0},
        "giveback_percent": {"green_min": -1.0, "amber_min": -5.0},
        "cost_variance_percent": {"green_max": 1.0, "amber_max": 5.0},
    },
    "industrial": {
        "on_time_delivery_percent": {"green_min": 92.0, "amber_min": 85.0},
        "on_time_pickup_percent": {"green_min": 92.0, "amber_min": 85.0},
        "tender_acceptance_rate": {"green_min": 90.0, "amber_min": 80.0},
        "claims_damage_ratio": {"green_max": 0.8, "amber_max": 1.5},
        "invoice_accuracy": {"green_min": 93.0, "amber_min": 88.0},
        "giveback_percent": {"green_min": -2.0, "amber_min": -6.0},
        "cost_variance_percent": {"green_max": 1.5, "amber_max": 6.0},
    },
    "healthcare": {
        "on_time_delivery_percent": {"green_min": 96.0, "amber_min": 92.0},
        "on_time_pickup_percent": {"green_min": 96.0, "amber_min": 92.0},
        "tender_acceptance_rate": {"green_min": 96.0, "amber_min": 88.0},
        "claims_damage_ratio": {"green_max": 0.3, "amber_max": 0.75},
        "invoice_accuracy": {"green_min": 97.0, "amber_min": 92.0},
        "giveback_percent": {"green_min": -1.0, "amber_min": -3.0},
        "cost_variance_percent": {"green_max": 0.5, "amber_max": 3.0},
    },
}

DEFAULT_SEGMENT = "retail"

STATUS_GREEN = "green"
STATUS_AMBER = "amber"
STATUS_RED = "red"
STATUS_UNKNOWN = "unknown"


def get_preset(segment: str) -> dict:
    """Return the threshold preset for a segment, defaulting to retail."""
    if not segment:
        return SEGMENT_PRESETS[DEFAULT_SEGMENT]
    key = str(segment).strip().lower()
    return SEGMENT_PRESETS.get(key, SEGMENT_PRESETS[DEFAULT_SEGMENT])


def _to_float(value):
    if value is None:
        return None
    try:
        return float(str(value).replace("%", "").replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def evaluate_threshold(metric_name: str, value, segment: str = DEFAULT_SEGMENT):
    """Return (status, threshold_dict) for a metric value against a segment preset."""
    preset = get_preset(segment)
    rule = preset.get(metric_name)
    if rule is None:
        return STATUS_UNKNOWN, None

    numeric = _to_float(value)
    if numeric is None:
        return STATUS_UNKNOWN, rule

    if "green_min" in rule:
        if numeric >= rule["green_min"]:
            return STATUS_GREEN, rule
        if numeric >= rule["amber_min"]:
            return STATUS_AMBER, rule
        return STATUS_RED, rule

    if "green_max" in rule:
        if numeric <= rule["green_max"]:
            return STATUS_GREEN, rule
        if numeric <= rule["amber_max"]:
            return STATUS_AMBER, rule
        return STATUS_RED, rule

    return STATUS_UNKNOWN, rule
