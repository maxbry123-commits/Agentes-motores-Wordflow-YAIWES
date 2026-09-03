import { NextResponse } from 'next/server'
import { z } from 'zod'

import { buildEvalEnvironmentPlan } from '@/lib/server/eval/environment-plan'
import { errorMessage } from '@/lib/shared-utils'

const PlanSchema = z.object({
  agentId: z.string().min(1),
  scenarioId: z.string().min(1).nullable().optional(),
  suite: z.string().min(1).nullable().optional(),
  gatewayProfileId: z.string().min(1).nullable().optional(),
  environmentId: z.string().min(1).nullable().optional(),
  refreshGateway: z.boolean().optional(),
})

function readBoolean(value: string | null): boolean {
  return value === '1' || value === 'true'
}

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const parsed = PlanSchema.safeParse({
      agentId: searchParams.get('agentId') || '',
      scenarioId: searchParams.get('scenarioId'),
      suite: searchParams.get('suite'),
      gatewayProfileId: searchParams.get('gatewayProfileId'),
      environmentId: searchParams.get('environmentId'),
      refreshGateway: readBoolean(searchParams.get('refreshGateway')),
    })
    if (!parsed.success) {
      return NextResponse.json(
        { error: parsed.error.issues.map((issue) => issue.message).join(', ') },
        { status: 400 },
      )
    }
    const plan = await buildEvalEnvironmentPlan(parsed.data)
    return NextResponse.json(plan)
  } catch (err: unknown) {
    return NextResponse.json({ error: errorMessage(err) }, { status: 500 })
  }
}

export async function POST(req: Request) {
  try {
    const body: unknown = await req.json()
    const parsed = PlanSchema.safeParse(body)
    if (!parsed.success) {
      return NextResponse.json(
        { error: parsed.error.issues.map((issue) => issue.message).join(', ') },
        { status: 400 },
      )
    }
    const plan = await buildEvalEnvironmentPlan(parsed.data)
    return NextResponse.json(plan)
  } catch (err: unknown) {
    return NextResponse.json({ error: errorMessage(err) }, { status: 500 })
  }
}
