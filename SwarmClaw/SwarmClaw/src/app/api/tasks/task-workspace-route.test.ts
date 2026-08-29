import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { after, before, test } from 'node:test'

import type { BoardTask } from '@/types'

const originalEnv = {
  DATA_DIR: process.env.DATA_DIR,
  WORKSPACE_DIR: process.env.WORKSPACE_DIR,
  SWARMCLAW_BUILD_MODE: process.env.SWARMCLAW_BUILD_MODE,
  SWARMCLAW_DAEMON_AUTOSTART: process.env.SWARMCLAW_DAEMON_AUTOSTART,
}

let tempDir = ''
let putTask: typeof import('./[id]/route')['PUT']
let getTaskHandoff: typeof import('./[id]/handoff/route')['GET']
let postTaskHandoff: typeof import('./[id]/handoff/route')['POST']
let getTaskExecutionPolicy: typeof import('./[id]/execution-policy/route')['GET']
let postTaskExecutionPolicy: typeof import('./[id]/execution-policy/route')['POST']
let postTaskRetry: typeof import('./[id]/retry/route')['POST']
let getTaskHandoffs: typeof import('./handoffs/route')['GET']
let getTasks: typeof import('./route')['GET']
let storage: typeof import('@/lib/server/storage')

function routeParams(id: string) {
  return { params: Promise.resolve({ id }) }
}

function seedTask(id: string, overrides: Partial<BoardTask> = {}) {
  const now = Date.now()
  storage.saveTasks({
    [id]: {
      id,
      title: 'Workspace Task',
      description: '',
      status: 'backlog',
      agentId: 'agent-1',
      createdAt: now,
      updatedAt: now,
      ...overrides,
    } as BoardTask,
  })
}

before(async () => {
  tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarmclaw-task-route-'))
  process.env.DATA_DIR = path.join(tempDir, 'data')
  process.env.WORKSPACE_DIR = path.join(tempDir, 'workspace')
  process.env.SWARMCLAW_BUILD_MODE = '1'
  process.env.SWARMCLAW_DAEMON_AUTOSTART = '0'
  storage = await import('@/lib/server/storage')
  putTask = (await import('./[id]/route')).PUT
  const handoffRoute = await import('./[id]/handoff/route')
  getTaskHandoff = handoffRoute.GET
  postTaskHandoff = handoffRoute.POST
  const policyRoute = await import('./[id]/execution-policy/route')
  getTaskExecutionPolicy = policyRoute.GET
  postTaskExecutionPolicy = policyRoute.POST
  postTaskRetry = (await import('./[id]/retry/route')).POST
  getTaskHandoffs = (await import('./handoffs/route')).GET
  getTasks = (await import('./route')).GET
})

after(() => {
  if (originalEnv.DATA_DIR === undefined) delete process.env.DATA_DIR
  else process.env.DATA_DIR = originalEnv.DATA_DIR
  if (originalEnv.WORKSPACE_DIR === undefined) delete process.env.WORKSPACE_DIR
  else process.env.WORKSPACE_DIR = originalEnv.WORKSPACE_DIR
  if (originalEnv.SWARMCLAW_BUILD_MODE === undefined) delete process.env.SWARMCLAW_BUILD_MODE
  else process.env.SWARMCLAW_BUILD_MODE = originalEnv.SWARMCLAW_BUILD_MODE
  if (originalEnv.SWARMCLAW_DAEMON_AUTOSTART === undefined) delete process.env.SWARMCLAW_DAEMON_AUTOSTART
  else process.env.SWARMCLAW_DAEMON_AUTOSTART = originalEnv.SWARMCLAW_DAEMON_AUTOSTART
  fs.rmSync(tempDir, { recursive: true, force: true })
})

test('PUT /api/tasks/:id provisions an execution workspace and preview links', async () => {
  seedTask('task-route-workspace', {
    title: 'Route Workspace',
    projectId: 'project-route',
    cwd: '/source/repo',
  })

  const response = await putTask(new Request('http://local/api/tasks/task-route-workspace', {
    method: 'PUT',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      provisionWorkspace: true,
      previewLinks: [{ label: 'Preview', url: 'http://127.0.0.1:3456', port: 3456 }],
      runtimeServices: [{ name: 'Next dev', status: 'planned', command: 'npm run dev', port: 3456 }],
    }),
  }), routeParams('task-route-workspace'))

  assert.equal(response.status, 200)
  const body = await response.json() as BoardTask
  assert.equal(body.executionWorkspace?.sourceCwd, '/source/repo')
  assert.equal(body.executionWorkspace?.context?.taskId, 'task-route-workspace')
  assert.equal(body.executionWorkspace?.envHints?.some((hint) => hint.key === 'WORKSPACE_CWD'), true)
  assert.equal(body.previewLinks?.[0]?.url, 'http://127.0.0.1:3456')
  assert.equal(body.runtimeServices?.[0]?.name, 'Next dev')
  assert.equal(fs.existsSync(body.executionWorkspace?.path || ''), true)
  assert.equal(fs.existsSync(body.executionWorkspace?.contextPath || ''), true)
  assert.equal(fs.existsSync(body.executionWorkspace?.envPath || ''), true)
})

test('GET /api/tasks returns computed blocked liveness without persisting a task patch', async () => {
  seedTask('task-blocked', {
    title: 'Blocked Route Task',
    status: 'backlog',
    blockedBy: ['dep-route'],
  })
  const tasks = storage.loadTasks()
  tasks['dep-route'] = {
    id: 'dep-route',
    title: 'Dependency',
    description: '',
    status: 'running',
    agentId: 'agent-1',
    createdAt: Date.now(),
    updatedAt: Date.now(),
  } as BoardTask
  storage.saveTasks(tasks)

  const response = await getTasks(new Request('http://local/api/tasks'))
  assert.equal(response.status, 200)
  const body = await response.json() as Record<string, BoardTask>
  assert.equal(body['task-blocked']?.liveness?.state, 'blocked')
  assert.deepEqual(body['task-blocked']?.liveness?.blockerTaskIds, ['dep-route'])
})

test('GET /api/tasks/:id/handoff returns readiness and markdown packets', async () => {
  seedTask('task-handoff', {
    title: 'Handoff Route Task',
    description: 'Prepare a packet.',
    blockedBy: ['dep-handoff'],
    qualityGate: {
      enabled: true,
      minResultChars: 50,
      minEvidenceItems: 1,
    },
  })
  const tasks = storage.loadTasks()
  tasks['dep-handoff'] = {
    id: 'dep-handoff',
    title: 'Dependency',
    description: '',
    status: 'running',
    agentId: 'agent-1',
    createdAt: Date.now(),
    updatedAt: Date.now(),
  } as BoardTask
  storage.saveTasks(tasks)

  const jsonResponse = await getTaskHandoff(
    new Request('http://local/api/tasks/task-handoff/handoff'),
    routeParams('task-handoff'),
  )
  assert.equal(jsonResponse.status, 200)
  const packet = await jsonResponse.json()
  assert.equal(packet.taskId, 'task-handoff')
  assert.equal(packet.readiness.status, 'blocked')
  assert.equal(packet.dependencies.blockedBy[0]?.id, 'dep-handoff')

  const markdownResponse = await getTaskHandoff(
    new Request('http://local/api/tasks/task-handoff/handoff?format=markdown'),
    routeParams('task-handoff'),
  )
  assert.equal(markdownResponse.status, 200)
  assert.match(markdownResponse.headers.get('content-type') || '', /text\/markdown/)
  const markdown = await markdownResponse.text()
  assert.match(markdown, /# Task Handoff: Handoff Route Task/)
  assert.match(markdown, /Readiness: blocked/)
})

test('PUT /api/tasks/:id blocks completion until execution policy stages are approved', async () => {
  seedTask('task-policy-complete', {
    title: 'Policy Completion Task',
    result: 'Implemented the requested feature, updated src/app/example.ts, and verified with npm run test.',
    executionPolicy: {
      enabled: true,
      mode: 'before_completion',
      stages: [{ id: 'review', title: 'Review', kind: 'review', requiredDecisions: 1 }],
    },
  })

  const blocked = await putTask(new Request('http://local/api/tasks/task-policy-complete', {
    method: 'PUT',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ status: 'completed' }),
  }), routeParams('task-policy-complete'))

  assert.equal(blocked.status, 409)
  assert.equal(storage.loadTasks()['task-policy-complete']?.status, 'backlog')

  const policyResponse = await postTaskExecutionPolicy(new Request('http://local/api/tasks/task-policy-complete/execution-policy', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ action: 'approve', actor: 'QA' }),
  }), routeParams('task-policy-complete'))
  assert.equal(policyResponse.status, 200)
  const policyBody = await policyResponse.json()
  assert.equal(policyBody.state.status, 'completed')

  const completed = await putTask(new Request('http://local/api/tasks/task-policy-complete', {
    method: 'PUT',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ status: 'completed' }),
  }), routeParams('task-policy-complete'))

  assert.equal(completed.status, 200)
  const body = await completed.json() as BoardTask
  assert.equal(body.status, 'completed')
})

test('PUT /api/tasks/:id allows edits to already completed tasks without re-requesting completion', async () => {
  seedTask('task-policy-completed-edit', {
    title: 'Completed Policy Edit Task',
    status: 'completed',
    result: 'Completed with tests passed and build passed.',
    executionPolicy: {
      enabled: true,
      mode: 'before_completion',
      stages: [{ id: 'review', title: 'Review', kind: 'review', requiredDecisions: 1 }],
    },
  })

  const response = await putTask(new Request('http://local/api/tasks/task-policy-completed-edit', {
    method: 'PUT',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ title: 'Completed Policy Edit Task Updated' }),
  }), routeParams('task-policy-completed-edit'))

  assert.equal(response.status, 200)
  const body = await response.json() as BoardTask
  assert.equal(body.status, 'completed')
  assert.equal(body.title, 'Completed Policy Edit Task Updated')
})

test('GET /api/tasks/:id/execution-policy returns policy summary', async () => {
  seedTask('task-policy-summary', {
    title: 'Policy Summary Task',
    executionPolicy: {
      enabled: true,
      mode: 'before_completion',
      stages: [{ id: 'review', title: 'Review', kind: 'review' }],
    },
  })

  const response = await getTaskExecutionPolicy(
    new Request('http://local/api/tasks/task-policy-summary/execution-policy'),
    routeParams('task-policy-summary'),
  )
  assert.equal(response.status, 200)
  const body = await response.json()
  assert.equal(body.summary.enabled, true)
  assert.equal(body.summary.status, 'waiting')
})

test('POST /api/tasks/:id/retry requeues a dead-lettered failed task', async () => {
  seedTask('task-dead-letter-retry', {
    title: 'Dead Letter Retry',
    status: 'failed',
    attempts: 3,
    maxAttempts: 3,
    retryScheduledAt: Date.now() + 60_000,
    deadLetteredAt: Date.now(),
    checkoutRunId: 'run-failed',
    error: 'Dead-lettered after 3/3 attempts: timeout',
    validation: { ok: false, reasons: ['No result'], checkedAt: Date.now() },
  })

  const response = await postTaskRetry(
    new Request('http://local/api/tasks/task-dead-letter-retry/retry', { method: 'POST' }),
    routeParams('task-dead-letter-retry'),
  )

  assert.equal(response.status, 200)
  const body = await response.json() as BoardTask
  assert.equal(body.status, 'queued')
  assert.equal(body.attempts, 0)
  assert.equal(body.retryScheduledAt, null)
  assert.equal(body.deadLetteredAt, null)
  assert.equal(body.checkoutRunId, null)
  assert.equal(body.error, null)
  assert.equal(body.validation, null)
  assert.equal(storage.loadQueue().includes('task-dead-letter-retry'), true)
  assert.equal(body.comments?.some((comment) => comment.text.includes('retry requested')), true)
})

test('POST /api/tasks/:id/retry rejects tasks still blocked by dependencies', async () => {
  seedTask('task-blocked-retry', {
    title: 'Blocked Retry',
    status: 'failed',
    blockedBy: ['retry-dep'],
    deadLetteredAt: Date.now(),
  })
  const tasks = storage.loadTasks()
  tasks['retry-dep'] = {
    id: 'retry-dep',
    title: 'Retry Dependency',
    description: '',
    status: 'running',
    agentId: 'agent-1',
    createdAt: Date.now(),
    updatedAt: Date.now(),
  } as BoardTask
  storage.saveTasks(tasks)

  const response = await postTaskRetry(
    new Request('http://local/api/tasks/task-blocked-retry/retry', { method: 'POST' }),
    routeParams('task-blocked-retry'),
  )

  assert.equal(response.status, 409)
  assert.equal(storage.loadTasks()['task-blocked-retry']?.status, 'failed')
  assert.equal(storage.loadQueue().includes('task-blocked-retry'), false)
})

test('POST /api/tasks/:id/handoff saves markdown and JSON snapshots into the workspace', async () => {
  seedTask('task-handoff-save', {
    title: 'Saved Handoff Task',
    cwd: '/source/repo',
    result: 'Ready for the next operator.',
  })

  const response = await postTaskHandoff(
    new Request('http://local/api/tasks/task-handoff-save/handoff', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ prepareWorkspace: true }),
    }),
    routeParams('task-handoff-save'),
  )

  assert.equal(response.status, 200)
  const body = await response.json()
  assert.equal(body.packet.taskId, 'task-handoff-save')
  assert.equal(fs.existsSync(body.files.markdownPath), true)
  assert.equal(fs.existsSync(body.files.jsonPath), true)
  assert.match(fs.readFileSync(body.files.markdownPath, 'utf8'), /# Task Handoff: Saved Handoff Task/)
})

test('GET /api/tasks/handoffs lists board-level readiness packets with counts', async () => {
  seedTask('task-ready', {
    title: 'Ready Task',
    executionWorkspace: {
      path: '/tmp/ready',
      mode: 'task',
      preparedAt: Date.now(),
      previewLinks: [],
      runtimeServices: [],
    },
  })
  seedTask('task-needs-attention', {
    title: 'Needs Workspace',
  })

  const response = await getTaskHandoffs(new Request('http://local/api/tasks/handoffs?status=needs_attention&limit=10'))
  assert.equal(response.status, 200)
  const body = await response.json()
  assert.equal(body.counts.ready >= 1, true)
  assert.equal(body.counts.needs_attention >= 1, true)
  assert.equal(body.items.every((packet: { readiness: { status: string } }) => packet.readiness.status === 'needs_attention'), true)
})
