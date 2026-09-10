import assert from 'node:assert/strict'
import test from 'node:test'

import { runWithTempDataDir } from '@/lib/server/test-utils/run-with-temp-data-dir'

test('GET /api/chats/[id]/context-pack returns structured and markdown handoff context', () => {
  const output = runWithTempDataDir<{
    status: number
    markdownStatus: number
    missingStatus: number
    schemaVersion: number
    linkedTaskCount: number
    recentMessageCount: number
    markdownContentType: string
    markdownIncludesTitle: boolean
    markdownIncludesTask: boolean
  }>(`
    const storageMod = await import('./src/lib/server/storage')
    const repoMod = await import('@/lib/server/messages/message-repository')
    const routeMod = await import('./src/app/api/chats/[id]/context-pack/route')
    const storage = storageMod.default || storageMod
    const repo = repoMod.default || repoMod
    const route = routeMod.default || routeMod

    const now = Date.now()
    storage.saveSessions({
      sess_pack_1: {
        id: 'sess_pack_1',
        name: 'Context pack test',
        cwd: process.env.WORKSPACE_DIR,
        user: 'tester',
        provider: 'openai',
        model: 'gpt-4o-mini',
        claudeSessionId: null,
        codexThreadId: 'codex-pack-thread',
        messages: [],
        createdAt: now,
        lastActiveAt: now,
        runContext: {
          objective: 'Hand off a release session.',
          constraints: ['Keep the pack short.'],
          keyFacts: ['The current tag is local only.'],
          discoveries: [],
          failedApproaches: [],
          currentPlan: ['Run checks'],
          completedSteps: [],
          blockers: [],
          parentContext: null,
          updatedAt: now,
          version: 1,
        },
      },
    })
    storage.saveTasks({
      task_pack_1: {
        id: 'task_pack_1',
        title: 'Verify context pack',
        description: 'Exercise API route.',
        status: 'running',
        sessionId: 'sess_pack_1',
        agentId: null,
        createdAt: now,
        updatedAt: now + 3,
      },
    })

    repo.appendMessage('sess_pack_1', { role: 'user', text: 'Prepare handoff.', time: now, attachedFiles: ['/tmp/handoff.md'] })
    repo.appendMessage('sess_pack_1', { role: 'assistant', text: 'Ready.', time: now + 1 })

    const response = await route.GET(
      new Request('http://local/api/chats/sess_pack_1/context-pack?messages=1'),
      { params: Promise.resolve({ id: 'sess_pack_1' }) },
    )
    const payload = await response.json()

    const markdownResponse = await route.GET(
      new Request('http://local/api/chats/sess_pack_1/context-pack?format=markdown'),
      { params: Promise.resolve({ id: 'sess_pack_1' }) },
    )
    const markdown = await markdownResponse.text()

    const missingResponse = await route.GET(
      new Request('http://local/api/chats/missing/context-pack'),
      { params: Promise.resolve({ id: 'missing' }) },
    )

    console.log(JSON.stringify({
      status: response.status,
      markdownStatus: markdownResponse.status,
      missingStatus: missingResponse.status,
      schemaVersion: payload.schemaVersion,
      linkedTaskCount: payload.linkedTasks.length,
      recentMessageCount: payload.recentMessages.length,
      markdownContentType: markdownResponse.headers.get('content-type') || '',
      markdownIncludesTitle: markdown.includes('# Session Context Pack: Context pack test'),
      markdownIncludesTask: markdown.includes('Verify context pack'),
    }))
  `, { prefix: 'swarmclaw-context-pack-route-' })

  assert.equal(output.status, 200)
  assert.equal(output.markdownStatus, 200)
  assert.equal(output.missingStatus, 404)
  assert.equal(output.schemaVersion, 1)
  assert.equal(output.linkedTaskCount, 1)
  assert.equal(output.recentMessageCount, 1)
  assert.match(output.markdownContentType, /text\/markdown/)
  assert.equal(output.markdownIncludesTitle, true)
  assert.equal(output.markdownIncludesTask, true)
})
