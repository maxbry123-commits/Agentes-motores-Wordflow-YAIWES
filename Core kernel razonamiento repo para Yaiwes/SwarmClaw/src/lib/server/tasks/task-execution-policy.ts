import { genId } from '@/lib/id'
import type {
  BoardTask,
  TaskExecutionPolicy,
  TaskExecutionPolicyDecision,
  TaskExecutionPolicyDecisionAction,
  TaskExecutionPolicyStage,
  TaskExecutionPolicyStageKind,
  TaskExecutionPolicyStageState,
  TaskExecutionPolicyState,
} from '@/types'

const STAGE_KINDS: TaskExecutionPolicyStageKind[] = ['review', 'approval', 'verification']
const DEFAULT_STAGE_TITLES: Record<TaskExecutionPolicyStageKind, string> = {
  review: 'Review',
  approval: 'Approval',
  verification: 'Verification',
}

function compactText(value: unknown, maxLen: number): string {
  if (typeof value !== 'string') return ''
  const compact = value.split(/\s+/).filter(Boolean).join(' ').trim()
  return compact.slice(0, maxLen)
}

function stableStageId(kind: TaskExecutionPolicyStageKind, index: number): string {
  return `${kind}-${index + 1}`
}

function normalizeStageKind(value: unknown): TaskExecutionPolicyStageKind {
  return STAGE_KINDS.includes(value as TaskExecutionPolicyStageKind)
    ? value as TaskExecutionPolicyStageKind
    : 'review'
}

function normalizeRequiredDecisions(value: unknown): number {
  const parsed = typeof value === 'number'
    ? value
    : typeof value === 'string'
      ? Number.parseInt(value, 10)
      : Number.NaN
  if (!Number.isFinite(parsed)) return 1
  return Math.max(1, Math.min(12, Math.trunc(parsed)))
}

function uniqueId(preferred: string, seen: Set<string>, fallback: string): string {
  const base = preferred || fallback
  if (!seen.has(base)) {
    seen.add(base)
    return base
  }
  let suffix = 2
  while (seen.has(`${base}-${suffix}`)) suffix += 1
  const id = `${base}-${suffix}`
  seen.add(id)
  return id
}

export function normalizeTaskExecutionPolicy(value: unknown, now = Date.now()): TaskExecutionPolicy | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null
  const input = value as Record<string, unknown>
  const enabled = input.enabled !== false
  const mode = input.mode === 'advisory' ? 'advisory' : 'before_completion'
  const rawStages = Array.isArray(input.stages) ? input.stages : []
  const seen = new Set<string>()
  const stages: TaskExecutionPolicyStage[] = []

  rawStages.forEach((entry, index) => {
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) return
    const row = entry as Record<string, unknown>
    const kind = normalizeStageKind(row.kind)
    const id = uniqueId(compactText(row.id, 80), seen, stableStageId(kind, index))
    const title = compactText(row.title, 120) || DEFAULT_STAGE_TITLES[kind]
    stages.push({
      id,
      title,
      kind,
      description: compactText(row.description, 500) || null,
      actorHint: compactText(row.actorHint, 160) || null,
      requiredDecisions: normalizeRequiredDecisions(row.requiredDecisions),
    })
  })

  if (!enabled || stages.length === 0) return null
  return {
    enabled: true,
    mode,
    stages: stages.slice(0, 12),
    createdAt: typeof input.createdAt === 'number' && Number.isFinite(input.createdAt) ? input.createdAt : now,
    updatedAt: now,
  }
}

function validDecisionAction(value: unknown): TaskExecutionPolicyDecisionAction | null {
  return value === 'approved' || value === 'changes_requested' || value === 'reset'
    ? value
    : null
}

function normalizeExistingDecision(value: unknown): TaskExecutionPolicyDecision | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null
  const row = value as Record<string, unknown>
  const stageId = compactText(row.stageId, 80)
  const action = validDecisionAction(row.action)
  if (!stageId || !action) return null
  return {
    id: compactText(row.id, 80) || genId(),
    stageId,
    action,
    actor: compactText(row.actor, 120) || 'operator',
    note: compactText(row.note, 1000) || null,
    decidedAt: typeof row.decidedAt === 'number' && Number.isFinite(row.decidedAt) ? row.decidedAt : Date.now(),
  }
}

function decisionsForPolicy(policy: TaskExecutionPolicy, existing?: TaskExecutionPolicyState | null): TaskExecutionPolicyDecision[] {
  const stageIds = new Set(policy.stages.map((stage) => stage.id))
  const raw = Array.isArray(existing?.decisions) ? existing.decisions : []
  return raw
    .map(normalizeExistingDecision)
    .filter((decision): decision is TaskExecutionPolicyDecision => !!decision && stageIds.has(decision.stageId))
    .sort((a, b) => a.decidedAt - b.decidedAt)
    .slice(-200)
}

function stageState(stage: TaskExecutionPolicyStage, decisions: TaskExecutionPolicyDecision[]): TaskExecutionPolicyStageState {
  const stageDecisions = decisions.filter((decision) => decision.stageId === stage.id)
  const last = stageDecisions[stageDecisions.length - 1] || null
  const latestResetIndex = stageDecisions.findLastIndex((decision) => decision.action === 'reset')
  const latestChangesIndex = stageDecisions.findLastIndex((decision) => decision.action === 'changes_requested')
  const activeDecisionStart = Math.max(latestResetIndex, latestChangesIndex) + 1
  const activeDecisions = stageDecisions.slice(activeDecisionStart)
  const requiredDecisions = normalizeRequiredDecisions(stage.requiredDecisions)
  const approvedDecisionCount = activeDecisions.filter((decision) => decision.action === 'approved').length
  if (last?.action === 'changes_requested') {
    return {
      id: stage.id,
      status: 'changes_requested',
      requiredDecisions,
      approvedDecisionCount,
      lastDecisionAt: last.decidedAt,
    }
  }
  if (approvedDecisionCount >= requiredDecisions) {
    return {
      id: stage.id,
      status: 'approved',
      requiredDecisions,
      approvedDecisionCount,
      lastDecisionAt: last?.decidedAt ?? null,
    }
  }
  return {
    id: stage.id,
    status: 'pending',
    requiredDecisions,
    approvedDecisionCount,
    lastDecisionAt: last?.decidedAt ?? null,
  }
}

export function syncTaskExecutionPolicyState(
  policy: TaskExecutionPolicy | null | undefined,
  existing?: TaskExecutionPolicyState | null,
  now = Date.now(),
): TaskExecutionPolicyState | null {
  if (!policy?.enabled || policy.stages.length === 0) return null
  const decisions = decisionsForPolicy(policy, existing)
  const stages = policy.stages.map((stage) => stageState(stage, decisions))
  const changeRequestedIndex = stages.findIndex((stage) => stage.status === 'changes_requested')
  const pendingIndex = stages.findIndex((stage) => stage.status === 'pending')

  if (changeRequestedIndex >= 0) {
    stages[changeRequestedIndex] = { ...stages[changeRequestedIndex], status: 'changes_requested' }
    return {
      status: 'changes_requested',
      currentStageId: stages[changeRequestedIndex].id,
      currentStageIndex: changeRequestedIndex,
      stages,
      decisions,
      updatedAt: now,
      completedAt: null,
    }
  }

  if (pendingIndex >= 0) {
    stages[pendingIndex] = { ...stages[pendingIndex], status: 'waiting' }
    return {
      status: 'waiting',
      currentStageId: stages[pendingIndex].id,
      currentStageIndex: pendingIndex,
      stages,
      decisions,
      updatedAt: now,
      completedAt: null,
    }
  }

  return {
    status: 'completed',
    currentStageId: null,
    currentStageIndex: null,
    stages,
    decisions,
    updatedAt: now,
    completedAt: existing?.completedAt || now,
  }
}

export function isTaskExecutionPolicySatisfied(task: Pick<BoardTask, 'executionPolicy' | 'executionPolicyState'>): boolean {
  const policy = task.executionPolicy || null
  if (!policy?.enabled || policy.mode === 'advisory') return true
  return task.executionPolicyState?.status === 'completed'
}

export function taskExecutionPolicyBlockReason(task: Pick<BoardTask, 'executionPolicy' | 'executionPolicyState'>): string | null {
  if (isTaskExecutionPolicySatisfied(task)) return null
  const policy = task.executionPolicy
  const state = task.executionPolicyState
  const stage = policy?.stages.find((item) => item.id === state?.currentStageId)
  if (state?.status === 'changes_requested') {
    return stage ? `Execution policy changes requested at ${stage.title}.` : 'Execution policy changes requested.'
  }
  return stage ? `Execution policy is waiting on ${stage.title}.` : 'Execution policy is waiting on a required stage.'
}

export function describeTaskExecutionPolicy(task: Pick<BoardTask, 'executionPolicy' | 'executionPolicyState'>): {
  enabled: boolean
  status: TaskExecutionPolicyState['status'] | 'disabled'
  currentStage: TaskExecutionPolicyStage | null
  remainingStages: number
  blockReason: string | null
} {
  const policy = task.executionPolicy || null
  const state = task.executionPolicyState || null
  const currentStage = policy?.stages.find((stage) => stage.id === state?.currentStageId) || null
  const remainingStages = state
    ? state.stages.filter((stage) => stage.status === 'pending' || stage.status === 'waiting' || stage.status === 'changes_requested').length
    : 0
  return {
    enabled: Boolean(policy?.enabled),
    status: state?.status || 'disabled',
    currentStage,
    remainingStages,
    blockReason: taskExecutionPolicyBlockReason(task),
  }
}

export interface RecordTaskExecutionPolicyDecisionInput {
  action: 'approve' | 'request_changes' | 'reset'
  stageId?: string | null
  actor?: string | null
  note?: string | null
}

export type RecordTaskExecutionPolicyDecisionResult =
  | { ok: true; task: BoardTask; decision: TaskExecutionPolicyDecision | null }
  | { ok: false; status: number; error: string }

export function recordTaskExecutionPolicyDecision(
  task: BoardTask,
  input: RecordTaskExecutionPolicyDecisionInput,
  now = Date.now(),
): RecordTaskExecutionPolicyDecisionResult {
  const policy = normalizeTaskExecutionPolicy(task.executionPolicy, now)
  if (!policy) return { ok: false, status: 400, error: 'Task execution policy is not enabled.' }
  const currentState = syncTaskExecutionPolicyState(policy, task.executionPolicyState, now)
  const stageId = compactText(input.stageId, 80) || currentState?.currentStageId || policy.stages[0]?.id || ''
  const stageIndex = policy.stages.findIndex((stage) => stage.id === stageId)
  if (stageIndex < 0) return { ok: false, status: 400, error: 'Execution policy stage not found.' }

  const existingDecisions = currentState?.decisions || []
  let nextDecisions = existingDecisions
  let decision: TaskExecutionPolicyDecision | null = null

  if (input.action === 'reset') {
    const stageIdsToReset = new Set(policy.stages.slice(stageIndex).map((stage) => stage.id))
    const resetDecisions = Array.from(stageIdsToReset).map((resetStageId): TaskExecutionPolicyDecision => ({
      id: genId(),
      stageId: resetStageId,
      action: 'reset',
      actor: compactText(input.actor, 120) || 'operator',
      note: compactText(input.note, 1000) || null,
      decidedAt: now,
    }))
    decision = resetDecisions[0] || null
    nextDecisions = [...existingDecisions, ...resetDecisions]
  } else {
    const note = compactText(input.note, 1000) || null
    if (input.action === 'request_changes' && !note) {
      return { ok: false, status: 400, error: 'A note is required when requesting changes.' }
    }
    decision = {
      id: genId(),
      stageId,
      action: input.action === 'approve' ? 'approved' : 'changes_requested',
      actor: compactText(input.actor, 120) || 'operator',
      note,
      decidedAt: now,
    }
    nextDecisions = [...existingDecisions, decision]
  }

  task.executionPolicy = { ...policy, updatedAt: now }
  task.executionPolicyState = syncTaskExecutionPolicyState(
    task.executionPolicy,
    {
      status: currentState?.status || 'waiting',
      currentStageId: currentState?.currentStageId || null,
      currentStageIndex: currentState?.currentStageIndex ?? null,
      stages: currentState?.stages || [],
      decisions: nextDecisions,
      updatedAt: now,
      completedAt: currentState?.completedAt || null,
    },
    now,
  )
  task.updatedAt = now
  return { ok: true, task, decision }
}
