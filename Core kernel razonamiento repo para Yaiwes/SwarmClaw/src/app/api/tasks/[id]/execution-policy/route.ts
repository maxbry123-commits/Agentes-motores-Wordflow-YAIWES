import { NextResponse } from 'next/server'
import { z } from 'zod'
import { notFound } from '@/lib/server/collection-helpers'
import { loadTask } from '@/lib/server/tasks/task-repository'
import { safeParseBody } from '@/lib/server/safe-parse-body'
import {
  describeTaskExecutionPolicy,
  normalizeTaskExecutionPolicy,
  syncTaskExecutionPolicyState,
} from '@/lib/server/tasks/task-execution-policy'
import { decideTaskExecutionPolicyFromRoute } from '@/lib/server/tasks/task-route-service'
import { formatZodError } from '@/lib/validation/schemas'

const TaskExecutionPolicyDecisionSchema = z.object({
  action: z.enum(['approve', 'request_changes', 'reset']).optional().default('approve'),
  stageId: z.string().optional(),
  actor: z.string().optional(),
  note: z.string().optional(),
})

export async function GET(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const task = loadTask(id)
  if (!task) return notFound()
  const policy = normalizeTaskExecutionPolicy(task.executionPolicy)
  const state = syncTaskExecutionPolicyState(policy, task.executionPolicyState)
  return NextResponse.json({
    taskId: id,
    policy,
    state,
    summary: describeTaskExecutionPolicy({ executionPolicy: policy, executionPolicyState: state }),
  })
}

export async function POST(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const { data: raw, error } = await safeParseBody<Record<string, unknown>>(req)
  if (error) return error
  const parsed = TaskExecutionPolicyDecisionSchema.safeParse(raw || {})
  if (!parsed.success) return NextResponse.json(formatZodError(parsed.error), { status: 400 })
  const result = decideTaskExecutionPolicyFromRoute(id, parsed.data)
  if (!result.ok && result.status === 404) return notFound()
  return result.ok
    ? NextResponse.json(result.payload)
    : NextResponse.json(result.payload, { status: result.status })
}
