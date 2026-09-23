import { z } from 'zod'

// We're keeping a simple non-relational schema here.
// IRL, you will have a schema for your data models.
export const taskSchema = z.object({
  id: z.string(),
  title: z.string(),
  status: z.string(),
  label: z.string(),
  priority: z.string(),
  // Extracted data. The poller writes this as a human-readable summary string
  // for some products (e.g. CarrierScorecard: "On-Time Delivery: 95% (green)")
  // and as a structured JSON object for others. Accept both — parsing as an
  // object only caused every row to throw and blank the page.
  details: z
    .union([z.record(z.string(), z.unknown()), z.string()])
    .nullable()
    .optional(),
  // Path in the 'uploads' bucket to the original document this record
  // came from, for verifying extraction against the source.
  source_file_path: z.string().nullable().optional(),
  // Optional deadline/expiration/renewal date, if this product has one.
  due_date: z.string().nullable().optional(),
})

export type Task = z.infer<typeof taskSchema>
