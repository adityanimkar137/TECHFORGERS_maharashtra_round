// Diagnosis for RUN-1024. Other failed runs get a generated diagnosis (see diagnosisApi.js).
export const mockDiagnosis = {
  runId: 'RUN-1024',
  primary: { stepIndex: 3, stepName: 'Extract Product Prices', probability: 0.87, confidence: 'High' },
  probabilities: [
    { step: 'Step 1', name: 'Understand Request', probability: 0.04 },
    { step: 'Step 2', name: 'Search Products', probability: 0.08 },
    { step: 'Step 3', name: 'Extract Product Prices', probability: 0.87 },
    { step: 'Step 4', name: 'Compare Prices', probability: 0.19 },
    { step: 'Step 5', name: 'Generate Answer', probability: 0.24 },
  ],
  evidence: [
    'Output differs from successful runs',
    'Abnormal numerical values detected (44.99, 3.999)',
    'Similar failed executions contained this pattern',
    'Step affects downstream comparison',
  ],
  relatedSuccessful: [
    { id: 'RUN-1021', note: 'Same extraction tool, prices parsed as integers' },
    { id: 'RUN-1017', note: 'Validated numeric output before ranking' },
    { id: 'RUN-1015', note: 'Plausible value range enforced' },
  ],
  relatedFailed: [
    { id: 'RUN-1019', note: 'Amounts parsed with wrong separator' },
    { id: 'RUN-1016', note: 'Unvalidated fare values reached comparison' },
  ],
}
