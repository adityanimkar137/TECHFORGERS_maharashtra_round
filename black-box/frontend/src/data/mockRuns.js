// Mock execution runs. Shape mirrors what the FastAPI backend should return.
// Step status: ok | suspicious | failed | skipped | running

const step = (n, name, tool, status, duration, o = {}) => ({
  id: `step-${n}`, index: n, name, tool, status, duration,
  timestamp: o.ts || '10:42:0' + n,
  checkpoint: o.checkpoint ?? `ckpt-${n}`,
  dependencies: o.deps ?? (n > 1 ? [`step-${n - 1}`] : []),
  input: o.input ?? {}, output: o.output ?? {}, expected: o.expected ?? null, error: o.error ?? null,
})

const generic = (names, failAt = null, runningAt = null) =>
  names.map((name, i) => {
    const n = i + 1
    let status = 'ok'
    if (failAt && n === failAt) status = 'failed'
    else if (failAt && n > failAt) status = 'skipped'
    if (runningAt && n === runningAt) status = 'running'
    else if (runningAt && n > runningAt) status = 'skipped'
    return step(n, name, ['llm.parse', 'http.search', 'python.extract', 'llm.reason', 'llm.write'][i % 5], status, status === 'skipped' ? 0 : 0.4 + i * 0.3, {
      input: { query: name }, output: status === 'ok' ? { result: 'ok' } : {},
      error: status === 'failed' ? 'Tool returned empty or malformed payload' : null,
    })
  })

const shoppingSteps = (fixed = false) => [
  step(1, 'Understand Request', 'llm.parse', 'ok', 0.6, {
    input: { user_request: 'Find cheapest laptop under ₹50,000' },
    output: { intent: 'find_cheapest_product', category: 'laptop', max_price: 50000, currency: 'INR' },
  }),
  step(2, 'Search Products', 'http.search', 'ok', 1.2, {
    input: { category: 'laptop', max_price: 50000 },
    output: { results: [
      { title: 'Acer Aspire 5', price_text: '₹44,990' },
      { title: 'HP 15s', price_text: '₹47,490' },
      { title: 'Lenovo IdeaPad Slim 3', price_text: '₹39,990' }] },
  }),
  step(3, 'Extract Product Prices', 'python.extract', fixed ? 'ok' : 'suspicious', fixed ? 1.3 : 0.9, {
    input: { products: ['Acer Aspire 5', 'HP 15s', 'Lenovo IdeaPad Slim 3'], raw_prices: ['₹44,990', '₹47,490', '₹39,990'] },
    output: fixed
      ? { prices: [44990, 47490, 39990], currency: 'INR', validated: true }
      : { prices: [44.99, 4749, 3.999], currency: 'INR', validated: false },
    expected: { prices: [44990, 47490, 39990], currency: 'INR' },
    error: fixed ? null : 'Thousands separator parsed as decimal point; values out of plausible range',
  }),
  step(4, 'Compare Prices', 'llm.reason', fixed ? 'ok' : 'failed', 0.8, {
    input: { prices: fixed ? [44990, 47490, 39990] : [44.99, 4749, 3.999] },
    output: fixed ? { cheapest: 'Lenovo IdeaPad Slim 3', price: 39990 } : { cheapest: 'HP 15s', price: 4749 },
    expected: { cheapest: 'Lenovo IdeaPad Slim 3', price: 39990 },
    error: fixed ? null : 'Comparison relied on corrupted upstream prices',
  }),
  step(5, 'Generate Answer', 'llm.write', fixed ? 'ok' : 'failed', 0.7, {
    input: { cheapest: fixed ? 'Lenovo IdeaPad Slim 3' : 'HP 15s' },
    output: { answer: fixed ? 'The cheapest laptop under ₹50,000 is the Lenovo IdeaPad Slim 3 at ₹39,990.' : 'The cheapest laptop is the HP 15s at ₹4,749.' },
    expected: { answer: 'The cheapest laptop under ₹50,000 is the Lenovo IdeaPad Slim 3 at ₹39,990.' },
    error: fixed ? null : 'Final answer contains incorrect price',
  }),
]

const run = (id, agent, task, status, duration, createdAt, steps, failure = null) =>
  ({ id, agent, task, status, duration, createdAt, steps, stepCount: steps.length, failure })

export const mockRuns = [
  run('RUN-1024', 'Shopping Agent', 'Find cheapest laptop under ₹50,000', 'FAILED', 4.8, '2026-10-03T10:42:00', shoppingSteps(false), 'Incorrect product prices'),
  run('RUN-1023', 'Support Agent', 'Summarise ticket #8841 and draft reply', 'SUCCESS', 3.2, '2026-10-03T10:31:00', generic(['Read Ticket', 'Search Knowledge Base', 'Extract Policy', 'Draft Reply'])),
  run('RUN-1022', 'Research Agent', 'Summarise latest EV battery papers', 'FAILED', 9.1, '2026-10-03T10:12:00', generic(['Understand Request', 'Search Papers', 'Extract Abstracts', 'Rank Papers', 'Write Summary'], 3), 'Tool timeout'),
  run('RUN-1021', 'Travel Agent', 'Plan 3-day Goa trip under ₹30,000', 'SUCCESS', 6.4, '2026-10-03T09:58:00', generic(['Understand Request', 'Search Hotels', 'Extract Prices', 'Build Itinerary', 'Generate Answer'])),
  run('RUN-1020', 'Shopping Agent', 'Compare 5G phones under ₹20,000', 'RUNNING', null, '2026-10-03T09:51:00', generic(['Understand Request', 'Search Products', 'Extract Prices', 'Compare Prices', 'Generate Answer'], null, 3)),
  run('RUN-1019', 'Finance Agent', 'Categorise September expenses', 'FAILED', 5.5, '2026-10-02T18:20:00', generic(['Load CSV', 'Parse Amounts', 'Categorise', 'Summarise'], 2), 'Schema mismatch'),
  run('RUN-1018', 'Support Agent', 'Refund eligibility check for order 5521', 'SUCCESS', 2.7, '2026-10-02T17:05:00', generic(['Read Order', 'Check Policy', 'Decide', 'Draft Reply'])),
  run('RUN-1017', 'Research Agent', 'Find top 3 vector databases', 'SUCCESS', 7.9, '2026-10-02T15:44:00', generic(['Understand Request', 'Search Web', 'Extract Facts', 'Rank', 'Write Summary'])),
  run('RUN-1016', 'Travel Agent', 'Cheapest train Nagpur to Pune', 'FAILED', 4.1, '2026-10-02T14:10:00', generic(['Understand Request', 'Search Trains', 'Extract Fares', 'Compare', 'Generate Answer'], 4), 'Hallucinated fare'),
  run('RUN-1015', 'Finance Agent', 'Estimate monthly SIP growth', 'SUCCESS', 3.9, '2026-10-02T11:32:00', generic(['Understand Request', 'Fetch Rates', 'Calculate', 'Generate Answer'])),
]

// Result of "Run Alternative" on RUN-1024 (not listed in the table until created).
export const mockAlternativeRuns = [
  run('RUN-1031', 'Shopping Agent', 'Find cheapest laptop under ₹50,000', 'SUCCESS', 5.4, '2026-10-03T11:05:00', shoppingSteps(true)),
]

export const dashboardStats = {
  totalRuns: 1248, successfulRuns: 1087, failedRuns: 161, diagnosedFailures: 118, replayTests: 64,
  executionSeries: [
    { day: 'Mon', success: 142, failed: 19 }, { day: 'Tue', success: 158, failed: 24 },
    { day: 'Wed', success: 171, failed: 22 }, { day: 'Thu', success: 149, failed: 31 },
    { day: 'Fri', success: 163, failed: 18 }, { day: 'Sat', success: 144, failed: 25 },
    { day: 'Sun', success: 160, failed: 22 },
  ],
  failureDistribution: [
    { name: 'Data extraction', value: 52 }, { name: 'Tool timeout', value: 34 },
    { name: 'Schema mismatch', value: 29 }, { name: 'Hallucination', value: 28 }, { name: 'Other', value: 18 },
  ],
}
