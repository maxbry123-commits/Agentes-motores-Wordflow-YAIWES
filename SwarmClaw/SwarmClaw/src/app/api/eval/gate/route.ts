import { NextResponse } from 'next/server'
import { evaluateEvalGate } from '@/lib/server/eval/baseline'
import { errorMessage } from '@/lib/shared-utils'

function parseNumberParam(value: string | null): number | null {
  if (value == null || value.trim() === '') return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const agentId = searchParams.get('agentId') || ''
    if (!agentId) {
      return NextResponse.json(
        { error: 'agentId is required' },
        { status: 400 },
      )
    }

    const result = evaluateEvalGate({
      agentId,
      scenarioId: searchParams.get('scenarioId'),
      suite: searchParams.get('suite'),
      minPercent: parseNumberParam(searchParams.get('minPercent')),
      maxRegressionPoints: parseNumberParam(searchParams.get('maxRegressionPoints')),
    })
    return NextResponse.json(result)
  } catch (err: unknown) {
    return NextResponse.json(
      { error: errorMessage(err) },
      { status: 500 },
    )
  }
}
