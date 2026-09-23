import csv
import io
import re
import json

from carrier_normalizer import normalize_carrier_name
from kpi_engine import (
    FIELD_ALIASES,
    KPI_DEFINITIONS,
    compute_record_kpis,
    _find_value,
)
from threshold_engine import (
    DEFAULT_SEGMENT,
    STATUS_GREEN,
    STATUS_AMBER,
    STATUS_RED,
    STATUS_UNKNOWN,
)


# Processed-row ids are a 64-bit signed autoincrement sequence starting at 1.
_ROW_COUNTER = {"next": 1}


def _next_id():
    value = _ROW_COUNTER["next"]
    _ROW_COUNTER["next"] = value + 1
    return value


STATUS_TO_TOP = {
    STATUS_GREEN: "green",
    STATUS_AMBER: "amber",
    STATUS_RED: "red",
    STATUS_UNKNOWN: "unknown",
}


def _to_float(value):
    if value is None:
        return None
    try:
        return float(str(value).replace("%", "").replace(",", "").replace("$", "").strip())
    except (TypeError, ValueError):
        return None


def _decode_bytes(file_bytes) -> str:
    if isinstance(file_bytes, str):
        return file_bytes
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return file_bytes.decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            continue
    return str(file_bytes)


def _extract_pdf_text(file_bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            return ""

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        chunks = []
        for page in reader.pages:
            chunks.append(page.extract_text() or "")
        return "\n".join(chunks)
    except Exception:
        return ""


def _parse_excel(file_bytes):
    try:
        import openpyxl
    except ImportError:
        return []

    rows = []
    try:
        workbook = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
    except Exception:
        return []

    for sheet in workbook.worksheets:
        table = []
        for row in sheet.iter_rows(values_only=True):
            table.append(list(row))
        rows.extend(_table_to_dicts(table))
    return rows


def _table_to_dicts(table):
    if not table:
        return []

    header_index = None
    for idx, row in enumerate(table[:10]):
        cells = [str(c).strip().lower() for c in row if c is not None and str(c).strip()]
        if len(cells) >= 3:
            header_index = idx
            break

    if header_index is None:
        return []

    header = [str(c).strip() if c is not None else "" for c in table[header_index]]
    dicts = []
    for row in table[header_index + 1:]:
        if row is None:
            continue
        if all(c is None or str(c).strip() == "" for c in row):
            continue
        record = {}
        for col, value in zip(header, row):
            if not col:
                continue
            record[col] = value
        if record:
            dicts.append(record)
    return dicts


def _parse_csv(text):
    try:
        reader = csv.reader(io.StringIO(text))
        table = [row for row in reader]
    except Exception:
        return []
    return _table_to_dicts(table)


def _parse_text_fallback(text):
    """Parse loosely structured text into record dicts using key: value lines."""
    records = []
    current = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                records.append(current)
                current = {}
            continue
        match = re.match(r"^([^:=]+)[:=]\s*(.+)$", line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            if key.lower() in ("carrier", "carrier name") and "carrier" in current:
                if current:
                    records.append(current)
                current = {}
            current[key] = value
    if current:
        records.append(current)
    return records


def _is_binary_container(data) -> bool:
    """True for formats whose raw bytes are not themselves scorecard text.

    Such bytes must never be fed to the ``key: value`` text fallback: PDF and
    zip (xlsx) syntax is full of ``:`` and ``=``, so the fallback happily
    fabricates placeholder records from binary noise instead of reporting that
    nothing was parseable.
    """
    return data[:4] == b"%PDF" or data[:2] == b"PK"


def _detect_and_parse(file_bytes):
    data = file_bytes if isinstance(file_bytes, (bytes, bytearray)) else str(file_bytes).encode("utf-8")

    if data[:4] == b"%PDF":
        text = _extract_pdf_text(data)
        if not text.strip():
            return []
        return _parse_text_fallback(text)

    if data[:2] == b"PK":
        return _parse_excel(data)

    text = _decode_bytes(data)
    parsed = _parse_csv(text)
    if parsed:
        return parsed

    return _parse_text_fallback(text)


def _build_details(row: dict, kpis: dict) -> str:
    parts = []
    carrier = kpis.get("carrier") or "Unknown carrier"
    parts.append(f"Carrier: {carrier}")
    if kpis.get("period"):
        parts.append(f"Period: {kpis['period']}")
    parts.append(f"Segment: {kpis['segment']}")
    for definition in KPI_DEFINITIONS:
        key = definition["key"]
        metric = kpis["scorecard"]["metrics"].get(key, {})
        value = metric.get("value")
        if value is None or str(value).strip() == "":
            continue
        parts.append(f"{definition['label']}: {value} ({metric.get('status', 'unknown')})")
    parts.append(f"Overall: {kpis['scorecard']['overall_status']}")
    return " | ".join(parts)


def _build_title(row: dict, kpis: dict) -> str:
    carrier = kpis.get("carrier") or "Unknown Carrier"
    period = kpis.get("period")
    if period:
        return f"{carrier} — {period} Carrier Scorecard"
    return f"{carrier} — Carrier Scorecard"


def _process_row(row: dict, default_segment: str) -> dict:
    kpis = compute_record_kpis(row, default_segment)
    overall = kpis["scorecard"]["overall_status"]
    top_status = STATUS_TO_TOP.get(overall, "unknown")

    period = kpis.get("period")
    due_date = None
    if period:
        due_date = str(period)

    return {
        "id": _next_id(),
        "title": _build_title(row, kpis),
        "status": top_status,
        "details": _build_details(row, kpis),
        "due_date": due_date,
        "carrier": kpis.get("carrier"),
        "carrier_raw": kpis.get("carrier_raw"),
        "carrier_confidence": kpis.get("carrier_confidence"),
        "segment": kpis.get("segment"),
        "period": period,
        "overall_status": overall,
        "scorecard": kpis["scorecard"],
    }


def process_file(file_bytes, segment: str = DEFAULT_SEGMENT) -> list:
    """Parse a carrier scorecard file and return normalized record dicts.

    Accepts PDF, Excel (.xlsx), CSV, or plain-text bytes. Returns a list of
    records each containing top-level title, status, details, and due_date,
    plus the computed carrier scorecard KPIs. Unparseable input returns an
    empty list rather than placeholder records.
    """
    if file_bytes is None:
        return []

    records = []
    for row in _detect_and_parse(file_bytes):
        if not isinstance(row, dict) or not row:
            continue
        records.append(_process_row(row, segment))

    return records


def reset_id_counter():
    _ROW_COUNTER["next"] = 1
