import assert from 'node:assert/strict'
import { describe, it } from 'node:test'

import type { BoardTask } from '@/types'
import {
  isTaskExecutionPolicySatisfied,
  normalizeTaskExecutionPolicy,
  recordTaskExecutionPolicyDecision,
  syncTaskExecutionPolicyState,
  taskExecutionPolicyBlockReason,
} from '@/lib/server/tasks/task-execution-policy'

function makeTask(overrides: Partial<BoardTask> = {}): BoardTask {
  return {
    id: 'task-1',
    title: 'Policy Task',
    description: '',
    status: 'backlog',
    agentId: 'agent-1',
    createdAt: 1,
    updatedAt: 1,
    ...overrides,
  } as BoardTask
}

describe('task execution policies', () => {
  it('normalizes ordered stages and initializes the first waiting stage', () => {
    const policy = normalizeTaskExecutionPolicy({
      enabled: true,
      stages: [
        { id: 'review', title: 'Review', kind: 'review' },
        { id: 'approval', title: 'Approval', kind: 'approval', requiredDecisions: 2 },
      ],
    }, 100)

    assert.equal(policy?.mode, 'before_completion')
    assert.equal(policy?.stages.length, 2)
    const state = syncTaskExecutionPolicyState(policy, null, 110)
    assert.equal(state?.status, 'waiting')
    assert.equal(state?.currentStageId, 'review')
    assert.equal(state?.stages[0]?.status, 'waiting')
    assert.equal(state?.stages[1]?.status, 'pending')
  })

  it('advances decisions through each required stage', () => {
    const task = makeTask({
      executionPolicy: normalizeTaskExecutionPolicy({
        stages: [
          { id: 'review', kind: 'review', title: 'Review' },
          { id: 'approval', kind: 'approval', title: 'Approval' },
        ],
      }, 100),
    })
    task.executionPolicyState = syncTaskExecutionPolicyState(task.executionPolicy, null, 100)

    const reviewed = recordTaskExecutionPolicyDecision(task, { action: 'approve', actor: 'Wayde' }, 200)
    assert.equal(reviewed.ok, true)
    assert.equal(task.executionPolicyState?.status, 'waiting')
    assert.equal(task.executionPolicyState?.currentStageId, 'approval')
    assert.equal(isTaskExecutionPolicySatisfied(task), false)

    const approved = recordTaskExecutionPolicyDecision(task, { action: 'approve', actor: 'Wayde' }, 300)
    assert.equal(approved.ok, true)
    assert.equal(task.executionPolicyState?.status, 'completed')
    assert.equal(isTaskExecutionPolicySatisfied(task), true)
  })

  it('blocks completion when changes are requested and supports stage reset', () => {
    const task = makeTask({
      executionPolicy: normalizeTaskExecutionPolicy({
        stages: [{ id: 'review', kind: 'review', title: 'Review' }],
      }, 100),
    })
    task.executionPolicyState = syncTaskExecutionPolicyState(task.executionPolicy, null, 100)

    const rejected = recordTaskExecutionPolicyDecision(task, {
      action: 'request_changes',
      actor: 'QA',
      note: 'Needs tests.',
    }, 200)
    assert.equal(rejected.ok, true)
    assert.equal(task.executionPolicyState?.status, 'changes_requested')
    assert.match(taskExecutionPolicyBlockReason(task) || '', /changes requested/i)

    const reset = recordTaskExecutionPolicyDecision(task, { action: 'reset', stageId: 'review' }, 300)
    assert.equal(reset.ok, true)
    assert.equal(task.executionPolicyState?.status, 'waiting')
    assert.equal(task.executionPolicyState?.decisions.length, 2)
    assert.equal(task.executionPolicyState?.decisions.at(-1)?.action, 'reset')
  })

  it('does not count approvals made before a later changes-requested decision', () => {
    const task = makeTask({
      executionPolicy: normalizeTaskExecutionPolicy({
        stages: [{ id: 'approval', kind: 'approval', title: 'Approval', requiredDecisions: 2 }],
      }, 100),
    })
    task.executionPolicyState = syncTaskExecutionPolicyState(task.executionPolicy, null, 100)

    const firstApproval = recordTaskExecutionPolicyDecision(task, { action: 'approve', actor: 'QA 1' }, 200)
    assert.equal(firstApproval.ok, true)
    assert.equal(task.executionPolicyState?.status, 'waiting')

    const rejected = recordTaskExecutionPolicyDecision(task, {
      action: 'request_changes',
      actor: 'QA 2',
      note: 'Needs another pass.',
    }, 300)
    assert.equal(rejected.ok, true)
    assert.equal(task.executionPolicyState?.status, 'changes_requested')

    const secondApproval = recordTaskExecutionPolicyDecision(task, { action: 'approve', actor: 'QA 1' }, 400)
    assert.equal(secondApproval.ok, true)
    assert.equal(task.executionPolicyState?.status, 'waiting')

    const finalApproval = recordTaskExecutionPolicyDecision(task, { action: 'approve', actor: 'QA 2' }, 500)
    assert.equal(finalApproval.ok, true)
    assert.equal(task.executionPolicyState?.status, 'completed')
  })
})
