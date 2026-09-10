import { NextResponse } from 'next/server'
import {
  getKnowledgeHygieneSummary,
  pruneArchivedKnowledgeSources,
  runKnowledgeHygieneMaintenance,
} from '@/lib/server/knowledge-sources'

export async function GET() {
  return NextResponse.json(await getKnowledgeHygieneSummary())
}

export async function POST(req: Request) {
  let body: Record<string, unknown> | null = null
  if ((req.headers.get('content-type') || '').includes('application/json')) {
    try {
      const parsed = await req.json()
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) body = parsed as Record<string, unknown>
    } catch {
      body = null
    }
  }

  if (body?.action === 'prune') {
    const olderThanDays = typeof body.olderThanDays === 'number' ? body.olderThanDays : null
    const result = await pruneArchivedKnowledgeSources({ olderThanDays })
    const summary = await getKnowledgeHygieneSummary()
    return NextResponse.json({ ...summary, prune: result })
  }

  return NextResponse.json(await runKnowledgeHygieneMaintenance())
}
