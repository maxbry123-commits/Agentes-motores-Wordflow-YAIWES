import assert from 'node:assert/strict'
import test, { afterEach } from 'node:test'

import { GET as getScheduleHistory } from './[id]/history/route'
import { loadSchedules, saveSchedules } from '@/lib/server/storage'

const originalSchedules = loadSchedules()

function routeParams(id: string) {
  return { params: Promise.resolve({ id }) }
}

afterEach(() => {
  saveSchedules(originalSchedules)
})

test('GET /api/schedules/[id]/history returns normalized revision history', async () => {
  const now = Date.now()
  saveSchedules({
    one: {
      id: 'one',
      name: 'History Schedule',
      agentId: 'schedule-route-agent-history',
      taskPrompt: 'Report changes',
      scheduleType: 'interval',
      intervalMs: 86_400_000,
      status: 'active',
      revision: 2,
      history: [{
        id: 'history-2',
        at: now,
        actor: 'user',
        action: 'updated',
        revision: 2,
        summary: 'Schedule updated: "History Schedule"',
        changes: [{
          field: 'status',
          label: 'Status',
          before: 'paused',
          after: 'active',
        }],
      }],
      createdAt: now,
      updatedAt: now,
    },
  })

  const response = await getScheduleHistory(
    new Request('http://local/api/schedules/one/history', { method: 'GET' }),
    routeParams('one'),
  )

  assert.equal(response.status, 200)
  const payload = await response.json() as Record<string, unknown>
  assert.equal(payload.scheduleId, 'one')
  assert.equal(payload.revision, 2)
  const history = payload.history as Array<Record<string, unknown>>
  assert.equal(history.length, 1)
  assert.equal(history[0].action, 'updated')
})
