import {
  getEvalBaselineForScope,
  listEvalBaselines,
  listEvalRunsByAgent,
  saveEvalBaseline,
} from './store'
import { getScenario, getSuiteScenarios } from './scenarios'
import type {
  EvalBaseline,
  EvalGateCheck,
  EvalGateResult,
  EvalGateScope,
  EvalGateScopeType,
  EvalRun,
} from './types'

const DEFAULT_MIN_PERCENT = 80
const DEFAULT_MAX_REGRESSION_POINTS = 5
const MAX_LOOKBACK_RUNS = 1_000

export interface EvalGateInput {
  agentId: string
  scenarioId?: string | null
  suite?: string | null
  minPercent?: number | null
  maxRegressionPoints?: number | null
}

export interface SetEvalBaselineInput extends EvalGateInput {
  label?: string | null
  notes?: string | null
}

interface EvalGateDeps {
  now?: () => number
  listRunsByAgent?: (agentId: string, limit: number) => EvalRun[]
  getBaselineForScope?: (agentId: string, scopeType: EvalGateScopeType, scopeId: string) => EvalBaseline | null
  saveBaseline?: (baseline: EvalBaseline) => void
  listBaselines?: (filters?: { agentId?: string; limit?: number }) => EvalBaseline[]
}

interface EvalAggregate {
  runs: EvalRun[]
  missingScenarioIds: string[]
  score: number
  maxScore: number
  percent: number | null
}

function normalizePercent(value: number | null | undefined, fallback: number): number {
  if (!Number.isFinite(value) || value == null) return fallback
  return Math.max(0, Math.min(100, Math.round(value)))
}

function normalizeRegressionPoints(value: number | null | undefined, fallback: number): number {
  if (!Number.isFinite(value) || value == null) return fallback
  return Math.max(0, Math.round(value))
}

function scorePercent(score: number, maxScore: number): number | null {
  if (!Number.isFinite(score) || !Number.isFinite(maxScore) || maxScore <= 0) return null
  return Math.round((score / maxScore) * 100)
}

function maxScoreForScenario(scenarioId: string): number {
  const scenario = getScenario(scenarioId)
  return scenario?.scoringCriteria.reduce((sum, criterion) => sum + criterion.weight, 0) ?? 0
}

export function resolveEvalGateScope(input: Pick<EvalGateInput, 'scenarioId' | 'suite'>): EvalGateScope {
  const scenarioId = input.scenarioId?.trim()
  if (scenarioId) {
    const scenario = getScenario(scenarioId)
    if (!scenario) throw new Error(`Unknown eval scenario: ${scenarioId}`)
    return {
      type: 'scenario',
      id: scenario.id,
      label: scenario.name,
      scenarioIds: [scenario.id],
    }
  }

  const suite = input.suite?.trim() || 'core'
  const scenarios = getSuiteScenarios(suite)
  if (scenarios.length === 0) throw new Error(`Unknown or empty eval suite: ${suite}`)
  return {
    type: 'suite',
    id: suite,
    label: suite,
    scenarioIds: scenarios.map((scenario) => scenario.id),
  }
}

export function evalBaselineId(agentId: string, scope: EvalGateScope): string {
  return `eval-baseline:${agentId}:${scope.type}:${scope.id}`
}

function latestRunsForScope(runs: EvalRun[], scope: EvalGateScope): EvalRun[] {
  const scenarioSet = new Set(scope.scenarioIds)
  const latest = new Map<string, EvalRun>()

  for (const run of runs) {
    if (!scenarioSet.has(run.scenarioId)) continue
    if (run.status === 'pending' || run.status === 'running') continue
    const previous = latest.get(run.scenarioId)
    if (!previous || (run.endedAt ?? run.startedAt) > (previous.endedAt ?? previous.startedAt)) {
      latest.set(run.scenarioId, run)
    }
  }

  return scope.scenarioIds
    .map((scenarioId) => latest.get(scenarioId))
    .filter(Boolean) as EvalRun[]
}

function aggregateRuns(scope: EvalGateScope, runs: EvalRun[]): EvalAggregate {
  const byScenario = new Map(runs.map((run) => [run.scenarioId, run]))
  const missingScenarioIds = scope.scenarioIds.filter((scenarioId) => !byScenario.has(scenarioId))
  const score = scope.scenarioIds.reduce((sum, scenarioId) => sum + (byScenario.get(scenarioId)?.score ?? 0), 0)
  const maxScore = scope.scenarioIds.reduce((sum, scenarioId) => {
    const runMaxScore = byScenario.get(scenarioId)?.maxScore
    return sum + (Number.isFinite(runMaxScore) && runMaxScore != null ? runMaxScore : maxScoreForScenario(scenarioId))
  }, 0)
  return {
    runs,
    missingScenarioIds,
    score,
    maxScore,
    percent: scorePercent(score, maxScore),
  }
}

function statusFromChecks(checks: EvalGateCheck[]): EvalGateResult['status'] {
  if (checks.some((check) => check.status === 'fail')) return 'fail'
  if (checks.some((check) => check.status === 'warn')) return 'warn'
  return 'pass'
}

export function listEvalBaselinesForAgent(agentId?: string | null, deps: EvalGateDeps = {}): EvalBaseline[] {
  const list = deps.listBaselines || listEvalBaselines
  return list({ agentId: agentId || undefined, limit: 200 })
}

export function setEvalBaseline(input: SetEvalBaselineInput, deps: EvalGateDeps = {}): EvalBaseline {
  if (!input.agentId.trim()) throw new Error('agentId is required')

  const now = deps.now?.() ?? Date.now()
  const scope = resolveEvalGateScope(input)
  const runs = latestRunsForScope(
    (deps.listRunsByAgent || listEvalRunsByAgent)(input.agentId, MAX_LOOKBACK_RUNS),
    scope,
  )
  const aggregate = aggregateRuns(scope, runs)
  if (aggregate.runs.length === 0) {
    throw new Error('Run the selected eval before setting a baseline.')
  }
  if (aggregate.missingScenarioIds.length > 0) {
    throw new Error(`Baseline requires latest runs for every scenario in scope. Missing: ${aggregate.missingScenarioIds.join(', ')}`)
  }

  const existing = (deps.getBaselineForScope || getEvalBaselineForScope)(input.agentId, scope.type, scope.id)
  const baseline: EvalBaseline = {
    id: existing?.id || evalBaselineId(input.agentId, scope),
    agentId: input.agentId,
    scope,
    baselineScore: aggregate.score,
    baselineMaxScore: aggregate.maxScore,
    baselinePercent: aggregate.percent ?? 0,
    minPercent: normalizePercent(input.minPercent, aggregate.percent ?? DEFAULT_MIN_PERCENT),
    maxRegressionPoints: normalizeRegressionPoints(input.maxRegressionPoints, existing?.maxRegressionPoints ?? DEFAULT_MAX_REGRESSION_POINTS),
    runIds: aggregate.runs.map((run) => run.id),
    label: input.label?.trim() || existing?.label || null,
    notes: input.notes?.trim() || existing?.notes || null,
    createdAt: existing?.createdAt || now,
    updatedAt: now,
  }

  ;(deps.saveBaseline || saveEvalBaseline)(baseline)
  return baseline
}

export function evaluateEvalGate(input: EvalGateInput, deps: EvalGateDeps = {}): EvalGateResult {
  if (!input.agentId.trim()) throw new Error('agentId is required')

  const generatedAt = deps.now?.() ?? Date.now()
  const scope = resolveEvalGateScope(input)
  const baseline = (deps.getBaselineForScope || getEvalBaselineForScope)(input.agentId, scope.type, scope.id)
  const runs = latestRunsForScope(
    (deps.listRunsByAgent || listEvalRunsByAgent)(input.agentId, MAX_LOOKBACK_RUNS),
    scope,
  )
  const aggregate = aggregateRuns(scope, runs)
  const minPercent = normalizePercent(input.minPercent, baseline?.minPercent ?? DEFAULT_MIN_PERCENT)
  const maxRegressionPoints = normalizeRegressionPoints(input.maxRegressionPoints, baseline?.maxRegressionPoints ?? DEFAULT_MAX_REGRESSION_POINTS)
  const regressionPoints = baseline && aggregate.percent != null
    ? Math.max(0, baseline.baselinePercent - aggregate.percent)
    : null

  const checks: EvalGateCheck[] = []
  if (aggregate.runs.length === 0) {
    checks.push({
      code: 'no_eval_runs',
      status: 'fail',
      message: 'No completed eval runs are available for this gate.',
    })
  }
  if (aggregate.missingScenarioIds.length > 0) {
    checks.push({
      code: 'missing_scope_runs',
      status: 'fail',
      message: `${aggregate.missingScenarioIds.length} scenario${aggregate.missingScenarioIds.length === 1 ? '' : 's'} have no latest run in this gate.`,
      detail: aggregate.missingScenarioIds.join(', '),
    })
  }
  if (aggregate.runs.some((run) => run.status === 'failed')) {
    checks.push({
      code: 'failed_eval_run',
      status: 'fail',
      message: 'At least one latest eval run failed.',
    })
  }
  if (aggregate.percent == null || aggregate.percent < minPercent) {
    checks.push({
      code: 'score_below_threshold',
      status: 'fail',
      message: `Current score is below the ${minPercent}% gate.`,
      detail: aggregate.percent == null ? 'n/a' : `${aggregate.percent}%`,
    })
  } else {
    checks.push({
      code: 'score_threshold_met',
      status: 'pass',
      message: `Current score meets the ${minPercent}% gate.`,
      detail: `${aggregate.percent}%`,
    })
  }
  if (!baseline) {
    checks.push({
      code: 'baseline_missing',
      status: 'warn',
      message: 'No approved baseline is set for this gate.',
    })
  } else if (regressionPoints != null && regressionPoints > maxRegressionPoints) {
    checks.push({
      code: 'regression_limit_exceeded',
      status: 'fail',
      message: `Regression exceeds the ${maxRegressionPoints} point allowance.`,
      detail: `${regressionPoints} points below baseline`,
    })
  } else if (regressionPoints != null) {
    checks.push({
      code: 'regression_within_limit',
      status: 'pass',
      message: `Regression is within the ${maxRegressionPoints} point allowance.`,
      detail: `${regressionPoints} point${regressionPoints === 1 ? '' : 's'} below baseline`,
    })
  }

  return {
    agentId: input.agentId,
    scope,
    status: statusFromChecks(checks),
    generatedAt,
    baseline,
    latestRuns: aggregate.runs,
    currentScore: aggregate.score,
    currentMaxScore: aggregate.maxScore,
    currentPercent: aggregate.percent,
    regressionPoints,
    minPercent,
    maxRegressionPoints,
    checks,
  }
}
