import assert from 'node:assert/strict'
import { describe, it } from 'node:test'

import {
  buildSessionContextPack,
  formatSessionContextPackMarkdown,
} from '@/lib/server/chats/session-context-pack'
import type { BoardTask, Message, Session } from '@/types'

function session(overrides: Partial<Session> = {}): Session {
  return {
    id: 'session-1',
    name: 'Release chat',
    cwd: '/workspace/release',
    user: 'operator',
    provider: 'claude-cli',
    model: 'claude-sonnet-4-6',
    claudeSessionId: null,
    messages: [],
    createdAt: 100,
    lastActiveAt: 200,
    agentId: 'agent-1',
    tools: ['shell', 'files'],
    extensions: ['release-kit'],
    runContext: {
      objective: 'Ship the next release.',
      constraints: ['Keep public notes concise.'],
      keyFacts: ['npm is already authenticated.'],
      discoveries: ['Desktop packaging is slow.'],
      failedApproaches: [],
      currentPlan: ['Run tests', 'Cut tag'],
      completedSteps: ['Bumped version'],
      blockers: [],
      parentContext: null,
      updatedAt: 250,
      version: 1,
    },
    ...overrides,
  } as Session
}

function message(overrides: Partial<Message> = {}): Message {
  return {
    role: 'user',
    text: 'Please prepare the release.',
    time: 300,
    ...overrides,
  }
}

function task(overrides: Partial<BoardTask> = {}): BoardTask {
  return {
    id: 'task-1',
    title: 'Release task',
    description: 'Prepare and verify the release.',
    status: 'running',
    agentId: 'agent-1',
    sessionId: 'session-1',
    createdAt: 120,
    updatedAt: 320,
    ...overrides,
  } as BoardTask
}

describe('session context packs', () => {
  it('builds a concise pack with linked tasks, attachments, resume handles, and recent visible turns', () => {
    const pack = buildSessionContextPack({
      session: session({
        codexThreadId: 'codex-thread-1',
        delegateResumeIds: { codex: 'delegate-codex-2' },
      }),
      messages: [
        message({ text: 'Visible user ask', attachedFiles: ['/tmp/spec.md'] }),
        message({ role: 'assistant', text: 'Hidden note', historyExcluded: true }),
        message({ role: 'assistant', text: 'Release plan ready.', toolEvents: [{ name: 'shell', input: 'npm test', output: 'passed' }] }),
      ],
      tasks: { 'task-1': task({ blockedBy: ['task-2'] }) },
      now: 500,
      maxRecentMessages: 8,
    })

    assert.equal(pack.schemaVersion, 1)
    assert.equal(pack.session.id, 'session-1')
    assert.equal(pack.status, 'attention')
    assert.equal(pack.linkedTasks.length, 1)
    assert.equal(pack.linkedTasks[0]?.id, 'task-1')
    assert.equal(pack.attachments[0]?.path, '/tmp/spec.md')
    assert.deepEqual(pack.resumeHandles.map((handle) => handle.kind), ['codex', 'codex-delegate'])
    assert.equal(pack.recentMessages.length, 2)
    assert.ok(pack.recentMessages.every((item) => !item.text.includes('Hidden note')))
    assert.ok(pack.nextActions.some((action) => action.includes('blocked linked task')))
  })

  it('renders markdown without provider reasoning, tool output dumps, or hidden transcript turns', () => {
    const pack = buildSessionContextPack({
      session: session(),
      messages: [
        message({ text: 'Need release context.' }),
        message({
          role: 'assistant',
          text: 'Here is the plan.',
          reasoningContent: 'private reasoning',
          thinking: 'internal thought stream',
          toolEvents: [{ name: 'shell', input: 'npm test', output: 'very long output that should not be rendered' }],
        }),
      ],
      tasks: { 'task-1': task({ status: 'completed', result: 'Release shipped.' }) },
      now: 800,
    })

    const markdown = formatSessionContextPackMarkdown(pack)

    assert.match(markdown, /# Session Context Pack: Release chat/)
    assert.match(markdown, /Provider: claude-cli/)
    assert.match(markdown, /Linked Tasks/)
    assert.match(markdown, /Recent Turns/)
    assert.doesNotMatch(markdown, /private reasoning/)
    assert.doesNotMatch(markdown, /internal thought stream/)
    assert.doesNotMatch(markdown, /very long output/)
  })
})
