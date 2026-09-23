from carrier_normalizer import normalize_carrier_name
from threshold_engine import evaluate_threshold, STATUS_GREEN, STATUS_AMBER, STATUS_RED
from processor import process_file, reset_id_counter


def test_normalizer_aliases():
    cases = {
        "UPS": "UPS",
        "u.p.s.": "UPS",
        "United Parcel Service": "UPS",
        "FedEx": "FedEx",
        "federal express": "FedEx",
        "DHL Express": "DHL",
        "United States Postal Service": "USPS",
    }
    for raw, expected in cases.items():
        normalized, confidence, _ = normalize_carrier_name(raw)
        assert normalized == expected, f"{raw} -> {normalized}, expected {expected}"
        assert confidence == 1.0, f"{raw} confidence {confidence}"

    unknown, confidence, matched = normalize_carrier_name("Acme Freight")
    assert unknown == "Acme Freight", f"unexpected unknown normalization: {unknown}"
    assert confidence == 0.0, f"unknown confidence should be 0.0, got {confidence}"
    assert matched is None
    print("OK: normalizer aliases")


def test_threshold_statuses():
    assert evaluate_threshold("on_time_delivery_percent", 96.0, "retail")[0] == STATUS_GREEN
    assert evaluate_threshold("on_time_delivery_percent", 92.0, "retail")[0] == STATUS_AMBER
    assert evaluate_threshold("on_time_delivery_percent", 80.0, "retail")[0] == STATUS_RED

    assert evaluate_threshold("claims_damage_ratio", 0.4, "retail")[0] == STATUS_GREEN
    assert evaluate_threshold("claims_damage_ratio", 0.8, "retail")[0] == STATUS_AMBER
    assert evaluate_threshold("claims_damage_ratio", 2.0, "retail")[0] == STATUS_RED

    assert evaluate_threshold("on_time_delivery_percent", 93.0, "industrial")[0] == STATUS_GREEN
    assert evaluate_threshold("on_time_delivery_percent", 93.0, "retail")[0] == STATUS_AMBER
    print("OK: threshold statuses")


def test_processor_parsing():
    reset_id_counter()
    csv_bytes = (
        "Carrier,On Time Delivery %,Claims Ratio,Invoice Accuracy %\n"
        "UPS,97.0,0.3,98.0\n"
        "FedEx,80.0,2.0,85.0\n"
    ).encode("utf-8")
    records = process_file(csv_bytes)
    assert isinstance(records, list)
    assert len(records) == 2, f"expected 2 records, got {len(records)}"
    assert records[0]["carrier"] == "UPS"
    assert records[0]["status"] == STATUS_GREEN
    assert records[1]["status"] == STATUS_RED
    for record in records:
        assert set(["title", "status", "details", "due_date"]).issubset(record.keys())
    print("OK: processor parsing")


def main():
    test_normalizer_aliases()
    test_threshold_statuses()
    test_processor_parsing()
    print("All tests passed.")


if __name__ == "__main__":
    main()
