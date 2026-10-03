export const strategies = [
  { id: 'basic', name: 'Basic Extraction', description: 'Original behaviour. Regex extraction without validation.', expectedOutcome: 'FAILED' },
  { id: 'validated', name: 'Validated Extraction', description: 'Normalises separators and validates values against a plausible range.', expectedOutcome: 'SUCCESS' },
  { id: 'strict', name: 'Strict Price Extraction', description: 'Locale-aware parsing, rejects any value outside the max price.', expectedOutcome: 'SUCCESS' },
]
export const defaultParams = { maxPrice: 50000, currency: 'INR', validation: true }
export const replayProgressSteps = [
  'Loading checkpoint state',
  'Restoring agent context',
  'Re-running Step 3 with selected strategy',
  'Re-running Step 4',
  'Re-running Step 5',
  'Recording alternative run',
]
