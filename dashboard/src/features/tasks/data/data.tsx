import {CircleCheckBig, Clock, TriangleAlert} from 'lucide-react'

export const labels = [
  {
    value: 'bug',
    label: 'Bug',
  },
  {
    value: 'feature',
    label: 'Feature',
  },
  {
    value: 'documentation',
    label: 'Documentation',
  },
]

// Severity tiers drive badge color. Every status maps to exactly one tier:
//   critical -> red (destructive)   e.g. expired, denied, failed
//   warning  -> amber (warning)     e.g. expiring soon, needs review
//   good     -> green (success)     e.g. valid, approved, done
//   neutral  -> gray (secondary)    e.g. pending, queued, n/a
export type Severity = 'critical' | 'warning' | 'good' | 'neutral'

export const severityToBadgeVariant: Record<Severity, 'destructive' | 'warning' | 'success' | 'secondary'> = {
  critical: 'destructive',
  warning: 'warning',
  good: 'success',
  neutral: 'secondary',
}

// PRODUCT_CUSTOMIZE: replace this list with the real statuses this product
// produces (must match exactly what the backend poller writes to
// records.status). Every status must declare a severity tier above. Default
// values below are generic placeholders only — do not ship as-is.
// __STATUSES_BLOCK_START__
export const statuses: {
  label: string
  value: string
  icon: typeof TriangleAlert
  severity: Severity
}[] = [
  { label: 'Uploaded', value: 'uploaded:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Parsing', value: 'parsing:info', icon: Clock, severity: 'info' as Severity },
  { label: 'Parsed', value: 'parsed:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Normalized', value: 'normalized:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Needs Review', value: 'needs_review:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Failed', value: 'failed:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Matched', value: 'matched:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Alias Normalized', value: 'alias_normalized:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Ambiguous', value: 'ambiguous:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Unmatched', value: 'unmatched:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Manually Confirmed', value: 'manually_confirmed:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Active', value: 'active:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Expired', value: 'expired:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Missing', value: 'missing:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Pending Review', value: 'pending_review:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Valid', value: 'valid:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Partial', value: 'partial:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Stale', value: 'stale:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Flagged Outlier', value: 'flagged_outlier:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Threshold Breached', value: 'threshold_breached:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Green', value: 'green:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Amber', value: 'amber:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Red', value: 'red:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Not Calibrated', value: 'not_calibrated:info', icon: Clock, severity: 'info' as Severity },
  { label: 'Cost Variance Flagged', value: 'cost_variance_flagged:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Missing Expected Rate', value: 'missing_expected_rate:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Duplicate', value: 'duplicate:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Disputed', value: 'disputed:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Paid', value: 'paid:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'None', value: 'none:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Open', value: 'open:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Approved', value: 'approved:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Denied', value: 'denied:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Complete', value: 'complete:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Missing Required Fields', value: 'missing_required_fields:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Carrier Name Unresolved', value: 'carrier_name_unresolved:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Period Mismatch', value: 'period_mismatch:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Duplicate Rows', value: 'duplicate_rows:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Currency Mismatch', value: 'currency_mismatch:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Draft', value: 'draft:info', icon: Clock, severity: 'info' as Severity },
  { label: 'Generated', value: 'generated:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Scheduled', value: 'scheduled:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Delivered', value: 'delivered:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Archived', value: 'archived:info', icon: Clock, severity: 'info' as Severity },
]
// __STATUSES_BLOCK_END__
