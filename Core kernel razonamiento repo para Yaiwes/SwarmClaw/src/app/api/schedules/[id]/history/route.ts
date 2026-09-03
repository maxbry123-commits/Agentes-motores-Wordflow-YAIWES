import { NextResponse } from 'next/server'
import { notFound } from '@/lib/server/collection-helpers'
import { loadSchedule } from '@/lib/server/schedules/schedule-repository'
import { normalizeScheduleHistory } from '@/lib/server/schedules/schedule-history'

export async function GET(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const schedule = loadSchedule(id)
  if (!schedule) return notFound()
  return NextResponse.json({
    scheduleId: schedule.id,
    revision: schedule.revision || 0,
    history: normalizeScheduleHistory(schedule.history),
  })
}
