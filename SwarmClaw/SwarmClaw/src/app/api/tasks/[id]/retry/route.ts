import { NextResponse } from 'next/server'
import { notFound } from '@/lib/server/collection-helpers'
import { retryTaskFromRoute } from '@/lib/server/tasks/task-route-service'

export async function POST(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const result = retryTaskFromRoute(id)
  if (!result.ok && result.status === 404) return notFound()
  return result.ok
    ? NextResponse.json(result.payload)
    : NextResponse.json(result.payload, { status: result.status })
}
