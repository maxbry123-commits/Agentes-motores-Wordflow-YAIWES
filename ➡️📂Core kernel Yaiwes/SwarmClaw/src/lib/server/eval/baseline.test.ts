import assert from 'node:assert/strict'
import test from 'node:test'

import {
  evaluateEvalGate,
  setEvalBaseline,
} from './baseline'
import type { EvalBaseline, EvalRun } from './types'

function makeRun(overrides: Partial<EvalRun> = {}): EvalRun {
  return {
    id: 'run-1',
    scenarioId: 'coding-prime',
    agentId: 'agent-1',
    status: 'completed',
    startedAt: 1,
    endedAt: 2,
    score: 8,
    maxScore: 10,
    details: [],
    ...overrides,
  }
}

function depsFor(runs: EvalRun[], baseline: EvalBaseline | null = null, saved: EvalBaseline[] = []) {
  return {
    now: () => 123,
    listRunsByAgent: (agentId: string) => runs.filter((run) => run.agentId === agentId),
    getBaselineForScope: () => baseline,
    saveBaseline: (next: EvalBaseline) => { saved.push(next) },
  }
}

test('setEvalBaseline snapshots the latest scenario score and gate defaults', () => {
  const saved: EvalBaseline[] = []
  const baseline = setEvalBaseline(
    {
      agentId: 'agent-1',
      scenarioId: 'coding-prime',
      minPercent: 75,
      maxRegressionPoints: 3,
      label: 'Release candidate',
    },
    depsFor([
      makeRun({ id: 'older', score: 4, startedAt: 1, endedAt: 2 }),
      makeRun({ id: 'latest', score: 8, startedAt: 5, endedAt: 6 }),
    ], null, saved),
  )

  assert.equal(saved.length, 1)
  assert.equal(baseline.scope.type, 'scenario')
  assert.equal(baseline.scope.id, 'coding-prime')
  assert.equal(baseline.baselinePercent, 80)
  assert.equal(baseline.minPercent, 75)
  assert.equal(baseline.maxRegressionPoints, 3)
  assert.deepEqual(baseline.runIds, ['latest'])
})

test('evaluateEvalGate warns until a baseline is approved', () => {
  const gate = evaluateEvalGate(
    { agentId: 'agent-1', scenarioId: 'coding-prime', minPercent: 70 },
    depsFor([makeRun({ score: 8, maxScore: 10 })]),
  )

  assert.equal(gate.currentPercent, 80)
  assert.equal(gate.status, 'warn')
  assert.ok(gate.checks.some((check) => check.code === 'baseline_missing' && check.status === 'warn'))
})

test('evaluateEvalGate fails when regression exceeds the baseline allowance', () => {
  const baseline = setEvalBaseline(
    { agentId: 'agent-1', scenarioId: 'coding-prime', minPercent: 70, maxRegressionPoints: 2 },
    depsFor([makeRun({ id: 'baseline', score: 9, maxScore: 10 })]),
  )

  const gate = evaluateEvalGate(
    { agentId: 'agent-1', scenarioId: 'coding-prime' },
    depsFor([makeRun({ id: 'current', score: 6, maxScore: 10, startedAt: 10, endedAt: 11 })], baseline),
  )

  assert.equal(gate.currentPercent, 60)
  assert.equal(gate.regressionPoints, 30)
  assert.equal(gate.status, 'fail')
  assert.ok(gate.checks.some((check) => check.code === 'regression_limit_exceeded'))
})

test('evaluateEvalGate passes when score and regression checks pass', () => {
  const baseline = setEvalBaseline(
    { agentId: 'agent-1', scenarioId: 'coding-prime', minPercent: 70, maxRegressionPoints: 5 },
    depsFor([makeRun({ id: 'baseline', score: 8, maxScore: 10 })]),
  )

  const gate = evaluateEvalGate(
    { agentId: 'agent-1', scenarioId: 'coding-prime' },
    depsFor([makeRun({ id: 'current', score: 8, maxScore: 10, startedAt: 10, endedAt: 11 })], baseline),
  )

  assert.equal(gate.status, 'pass')
  assert.equal(gate.regressionPoints, 0)
  assert.ok(gate.checks.some((check) => check.code === 'score_threshold_met'))
})

test('suite gates require latest runs for every scenario in scope before baselining', () => {
  assert.throws(
    () => setEvalBaseline(
      { agentId: 'agent-1', suite: 'core' },
      depsFor([makeRun({ scenarioId: 'coding-prime' })]),
    ),
    /Baseline requires latest runs for every scenario in scope/,
  )
})
