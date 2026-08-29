import assert from 'node:assert/strict'
import { describe, it } from 'node:test'

import { computeTaskFingerprint } from '@/lib/task-dedupe'
import type { BoardTask } from '@/types'
import {
  applyTaskPatch,
  prepareTaskCreation,
  resolveAssignmentWorkflowStateTransition,
} from '@/lib/server/tasks/task-service'

function makeTask(overrides: Partial<BoardTask> = {}): BoardTask {
  return {
    id: 'task-1',
    title: 'Example Task',
    description: 'Do the work',
    status: 'backlog',
    agentId: 'agent-1',
    sessionId: null,
    result: null,
    error: null,
    createdAt: 1,
    updatedAt: 1,
    queuedAt: null,
    startedAt: null,
    completedAt: null,
    ...overrides,
  }
}

describe('task service helpers', () => {
  it('prepareTaskCreation derives a title and normalizes running to queued', () => {
    const prepared = prepareTaskCreation({
      id: 'task-create',
      input: {
        description: 'Please create a new login page for the app.',
        status: 'running',
        agentId: 'agent-1',
      },
      tasks: {},
      now: 50,
      deriveTitleFromDescription: true,
      requireMeaningfulTitle: true,
    })

    assert.equal(prepared.ok, true)
    if (!prepared.ok) return
    assert.equal(prepared.duplicate, null)
    assert.equal(prepared.task.title, 'a new login page for the app.')
    assert.equal(prepared.task.status, 'queued')
    assert.equal((prepared.task.fingerprint || '').length, 16)
  })

  it('prepareTaskCreation returns an existing duplicate task instead of a new one', () => {
    const existing = makeTask({
      id: 'existing-task',
      title: 'Unique dedupe title',
      agentId: 'agent-1',
      fingerprint: computeTaskFingerprint('Unique dedupe title', 'agent-1'),
    })
    const prepared = prepareTaskCreation({
      id: 'task-create',
      input: {
        title: 'Unique dedupe title',
        description: 'Duplicate task',
        agentId: 'agent-1',
      },
      tasks: { 'existing-task': existing },
      now: 60,
    })

    assert.equal(prepared.ok, true)
    if (!prepared.ok) return
    assert.equal(prepared.duplicate?.id, 'existing-task')
  })

  it('applyTaskPatch strips invalid statuses and clears nullable project ids', () => {
    const task = makeTask({
      status: 'backlog',
      projectId: 'project-1',
    })

    applyTaskPatch({
      task,
      patch: {
        status: 'bananas',
        projectId: null,
      },
      now: 75,
      clearProjectIdWhenNull: true,
    })

    assert.equal(task.status, 'backlog')
    assert.equal('projectId' in task, false)
    assert.equal(task.updatedAt, 75)
  })

  it('applyTaskPatch normalizes running updates to queued', () => {
    const task = makeTask({
      status: 'backlog',
    })

    applyTaskPatch({
      task,
      patch: { status: 'running' },
      now: 90,
    })

    assert.equal(task.status, 'queued')
  })
})

describe('task-service assignment workflow transitions', () => {
  it('moves newly assigned backlog workflow tasks to in_progress without queueing runtime work', () => {
    const task = makeTask({ agentId: '', workflowStateId: 'backlog' })
    applyTaskPatch({
      task,
      patch: { agentId: 'agent-builder' },
      now: 100,
    })

    assert.equal(task.agentId, 'agent-builder')
    assert.equal(task.status, 'backlog')
    assert.equal(task.workflowStateId, 'in_progress')
    assert.equal(task.updatedAt, 100)
  })

  it('preserves explicit workflow state patches', () => {
    const task = makeTask({ workflowStateId: 'todo' })
    applyTaskPatch({
      task,
      patch: { agentId: 'agent-builder', workflowStateId: 'needs_review' },
      now: 100,
    })

    assert.equal(task.workflowStateId, 'needs_review')
  })

  it('seeds assigned task creation into the in_progress workflow lane', () => {
    const prepared = prepareTaskCreation({
      input: {
        title: 'Build the client',
        description: '',
        agentId: 'builder',
      },
      tasks: {},
      now: 200,
    })

    assert.equal(prepared.ok, true)
    if (prepared.ok) {
      assert.equal(prepared.task.status, 'backlog')
      assert.equal(prepared.task.workflowStateId, 'in_progress')
    }
  })

  it('auto-queues agent-created tasks delegated to a different agent', () => {
    const prepared = prepareTaskCreation({
      input: {
        title: 'Build delegated client',
        description: 'Hand this work to the builder.',
        agentId: 'builder',
      },
      tasks: {},
      now: 210,
      creatorAgentId: 'coordinator',
      autoQueueDelegatedTasks: true,
    })

    assert.equal(prepared.ok, true)
    if (!prepared.ok) return
    assert.equal(prepared.task.status, 'queued')
    assert.equal(prepared.task.agentId, 'builder')
  })

  it('does not auto-queue self-assigned or explicitly backlogged tasks', () => {
    const selfAssigned = prepareTaskCreation({
      input: {
        title: 'Self task',
        description: '',
        agentId: 'coordinator',
      },
      tasks: {},
      now: 220,
      creatorAgentId: 'coordinator',
      autoQueueDelegatedTasks: true,
    })
    assert.equal(selfAssigned.ok, true)
    if (selfAssigned.ok) assert.equal(selfAssigned.task.status, 'backlog')

    const explicitBacklog = prepareTaskCreation({
      input: {
        title: 'Explicit backlog',
        description: '',
        agentId: 'builder',
        status: 'backlog',
      },
      tasks: {},
      now: 230,
      creatorAgentId: 'coordinator',
      autoQueueDelegatedTasks: true,
    })
    assert.equal(explicitBacklog.ok, true)
    if (explicitBacklog.ok) assert.equal(explicitBacklog.task.status, 'backlog')
  })

  it('leaves already-started workflow states alone', () => {
    const next = resolveAssignmentWorkflowStateTransition({
      previousAgentId: '',
      nextAgentId: 'agent-builder',
      previousWorkflowStateId: 'needs_review',
    })

    assert.equal(next, null)
  })
})
