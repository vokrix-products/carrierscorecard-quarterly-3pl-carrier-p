# CarrierScorecard

CarrierScorecard is a quarterly 3PL/carrier performance report builder. It ingests raw carrier scorecard data (PDF, Excel, CSV, or plain text), normalizes messy carrier names to canonical providers, and evaluates each carrier KPI against segment-aware green/amber/red thresholds.

## Product Archetype

This is a **report-builder / document-extraction** backend. It takes an uploaded file containing carrier performance metrics and returns structured, scored records ready to render into a quarterly scorecard review.

## Modules

- `carrier_normalizer.py` — normalizes raw carrier names (e.g. `UPS`, `U.P.S.`, `United Parcel Service`) to canonical values via `normalize_carrier_name()`, returning `(normalized, confidence, matched_alias)`. Exact alias matches return confidence `1.0`; unknown names pass through cleaned with confidence `0.0`.
- `threshold_engine.py` — segment-aware threshold presets (`retail`, `industrial`, `healthcare`) for every KPI, exposing `evaluate_threshold(metric, value, segment)` returning `green`/`amber`/`red`/`unknown`.
- `kpi_engine.py` — standard carrier scorecard KPI calculations and per-record compute/placeholder helpers. Highest-to-lowest rollup: any red makes the carrier red.
- `processor.py` — main entry point. Defines `process_file(file_bytes) -> list[dict]`, parses PDF/Excel/CSV/text, extracts fields, normalizes carriers, applies flags, and returns records with top-level `title`, `status`, `details`, and `due_date`.
- `run_demo.py` — zero-argument demo using hardcoded CSV bytes; asserts a list result and exits 0.
- `run_tests.py` — zero-argument tests for parsing, alias normalization, and threshold statuses.

## KPIs Evaluated

- On-Time Delivery %
- On-Time Pickup %
- Tender Acceptance Rate
- Claims/Damage Ratio
- Invoice Accuracy %
- Giveback %
- Cost Variance %

## Record Shape

Each returned record includes:

- `title` — e.g. `UPS — Q1 2025 Carrier Scorecard`
- `status` — rollup status: `green`, `amber`, `red`, or `unknown`
- `details` — human-readable summary of every KPI and its status
- `due_date` — reporting period (or null when absent)
- `carrier`, `carrier_raw`, `carrier_confidence`, `segment`, `period`, `overall_status`, `scorecard`

## Running

```bash
pip install -r requirements.txt
python3 run_demo.py
python3 run_tests.py
```

## What the Poller Expects as Input

The poller feeds a single file to `process_file()`:

- **Accepted formats:** PDF (`.pdf`), Excel (`.xlsx`), CSV (`.csv`), or plain text (`.txt`).
- **CSV/Excel shape:** a header row containing a carrier column (e.g. `Carrier`) plus one column per KPI. Column names are matched case-insensitively against known aliases (`On Time Delivery %`, `Tender Acceptance Rate`, `Claims Ratio`, etc.).
- **Optional columns:** `Period`/`Quarter` populates `due_date`; `Segment` selects the threshold preset (`retail`, `industrial`, `healthcare`); defaults to `retail` when absent.
- **Text fallback:** loosely structured `Key: Value` lines are parsed when tabular parsing yields nothing.
- **Bytes in, records out:** `process_file(file_bytes)` always returns a list of dicts, including for unparseable input (empty list).

## Reused Across All Vokrix Products

The normalizer, threshold engine, and KPI engine are shared building blocks reused across every Vokrix report-builder backend.

Dashboard: https://carrierscorecard-quarterly-3pl-carrier-p.vokrix.co
Vercel: carrierscorecard-quarterly-3pl-carrier-p
Railway: carrierscorecard-quarterly-3pl-carrier-p
Cloudflare: carrierscorecard-quarterly-3pl-carrier-p.vokrix.co

Billing: price_1UIe2L2c9uGCcgMSteIpJ74J

Landing: https://vokrix.co/carrierscorecard-quarterly-3pl-carrier-p

Outreach: active
