import { NextResponse } from 'next/server'
import { z } from 'zod'
import { evaluateEvalGate, listEvalBaselinesForAgent, setEvalBaseline } from '@/lib/server/eval/baseline'
import { errorMessage } from '@/lib/shared-utils'

const BaselineSchema = z.object({
  agentId: z.string().min(1),
  scenarioId: z.string().min(1).nullable().optional(),
  suite: z.string().min(1).nullable().optional(),
  minPercent: z.number().min(0).max(100).nullable().optional(),
  maxRegressionPoints: z.number().min(0).max(100).nullable().optional(),
  label: z.string().max(160).nullable().optional(),
  notes: z.string().max(1_000).nullable().optional(),
})

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const agentId = searchParams.get('agentId')
    return NextResponse.json(listEvalBaselinesForAgent(agentId))
  } catch (err: unknown) {
    return NextResponse.json(
      { error: errorMessage(err) },
      { status: 500 },
    )
  }
}

export async function POST(req: Request) {
  try {
    const body: unknown = await req.json()
    const parsed = BaselineSchema.safeParse(body)
    if (!parsed.success) {
      return NextResponse.json(
        { error: parsed.error.issues.map((issue) => issue.message).join(', ') },
        { status: 400 },
      )
    }

    const baseline = setEvalBaseline(parsed.data)
    const gate = evaluateEvalGate({
      agentId: parsed.data.agentId,
      scenarioId: parsed.data.scenarioId,
      suite: parsed.data.suite,
      minPercent: parsed.data.minPercent,
      maxRegressionPoints: parsed.data.maxRegressionPoints,
    })
    return NextResponse.json({ baseline, gate })
  } catch (err: unknown) {
    return NextResponse.json(
      { error: errorMessage(err) },
      { status: 500 },
    )
  }
}
