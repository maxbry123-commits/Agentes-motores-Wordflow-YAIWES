import { NextResponse } from 'next/server'

import { buildSessionContextPack, formatSessionContextPackMarkdown } from '@/lib/server/chats/session-context-pack'
import { notFound } from '@/lib/server/collection-helpers'
import { getMessages } from '@/lib/server/messages/message-repository'
import { getSession } from '@/lib/server/sessions/session-repository'
import { listTasks } from '@/lib/server/tasks/task-repository'

const DEFAULT_RECENT_MESSAGES = 12
const MAX_RECENT_MESSAGES = 40

function parseMaxRecentMessages(req: Request): number {
  const url = new URL(req.url)
  const raw = url.searchParams.get('messages') || url.searchParams.get('maxRecentMessages')
  const parsed = Number.parseInt(raw || '', 10)
  if (!Number.isFinite(parsed)) return DEFAULT_RECENT_MESSAGES
  return Math.max(1, Math.min(MAX_RECENT_MESSAGES, parsed))
}

export async function GET(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const session = getSession(id)
  if (!session) return notFound()

  const url = new URL(req.url)
  const format = url.searchParams.get('format')
  const pack = buildSessionContextPack({
    session,
    messages: getMessages(id),
    tasks: listTasks(),
    maxRecentMessages: parseMaxRecentMessages(req),
  })

  if (format === 'markdown') {
    return new Response(formatSessionContextPackMarkdown(pack), {
      headers: {
        'content-type': 'text/markdown; charset=utf-8',
      },
    })
  }

  return NextResponse.json(pack)
}
