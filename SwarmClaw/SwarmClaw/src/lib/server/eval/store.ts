import Database from 'better-sqlite3'
import path from 'path'
import type { EvalBaseline, EvalRun } from './types'
import { DATA_DIR } from '../data-dir'

const DB_PATH = path.join(DATA_DIR, 'eval-runs.db')

let db: Database.Database | null = null

function getDb(): Database.Database {
  if (!db) {
    db = new Database(DB_PATH)
    db.pragma('journal_mode = WAL')
    db.exec(`CREATE TABLE IF NOT EXISTS eval_runs (
      id TEXT PRIMARY KEY,
      data TEXT NOT NULL
    )`)
    db.exec(`CREATE TABLE IF NOT EXISTS eval_baselines (
      id TEXT PRIMARY KEY,
      agent_id TEXT NOT NULL,
      scope_type TEXT NOT NULL,
      scope_id TEXT NOT NULL,
      data TEXT NOT NULL,
      updated_at INTEGER NOT NULL
    )`)
    db.exec('CREATE INDEX IF NOT EXISTS idx_eval_baselines_agent ON eval_baselines(agent_id, scope_type, scope_id)')
  }
  return db
}

export function saveEvalRun(run: EvalRun): void {
  getDb().prepare('INSERT OR REPLACE INTO eval_runs (id, data) VALUES (?, ?)').run(run.id, JSON.stringify(run))
}

export function getEvalRun(id: string): EvalRun | null {
  const row = getDb().prepare('SELECT data FROM eval_runs WHERE id = ?').get(id) as { data: string } | undefined
  return row ? JSON.parse(row.data) as EvalRun : null
}

export function listEvalRuns(limit = 50): EvalRun[] {
  const rows = getDb().prepare('SELECT data FROM eval_runs ORDER BY rowid DESC LIMIT ?').all(limit) as { data: string }[]
  return rows.map(r => JSON.parse(r.data) as EvalRun)
}

export function listEvalRunsByAgent(agentId: string, limit = 50): EvalRun[] {
  return listEvalRuns(limit * 2).filter(r => r.agentId === agentId).slice(0, limit)
}

export function saveEvalBaseline(baseline: EvalBaseline): void {
  getDb().prepare(`
    INSERT OR REPLACE INTO eval_baselines (id, agent_id, scope_type, scope_id, data, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(
    baseline.id,
    baseline.agentId,
    baseline.scope.type,
    baseline.scope.id,
    JSON.stringify(baseline),
    baseline.updatedAt,
  )
}

export function getEvalBaseline(id: string): EvalBaseline | null {
  const row = getDb().prepare('SELECT data FROM eval_baselines WHERE id = ?').get(id) as { data: string } | undefined
  return row ? JSON.parse(row.data) as EvalBaseline : null
}

export function getEvalBaselineForScope(agentId: string, scopeType: EvalBaseline['scope']['type'], scopeId: string): EvalBaseline | null {
  const row = getDb().prepare(`
    SELECT data FROM eval_baselines
    WHERE agent_id = ? AND scope_type = ? AND scope_id = ?
    ORDER BY updated_at DESC
    LIMIT 1
  `).get(agentId, scopeType, scopeId) as { data: string } | undefined
  return row ? JSON.parse(row.data) as EvalBaseline : null
}

export function listEvalBaselines(filters: { agentId?: string; limit?: number } = {}): EvalBaseline[] {
  const limit = Math.max(1, Math.min(filters.limit ?? 100, 500))
  const rows = filters.agentId
    ? getDb().prepare('SELECT data FROM eval_baselines WHERE agent_id = ? ORDER BY updated_at DESC LIMIT ?').all(filters.agentId, limit) as { data: string }[]
    : getDb().prepare('SELECT data FROM eval_baselines ORDER BY updated_at DESC LIMIT ?').all(limit) as { data: string }[]
  return rows.map((row) => JSON.parse(row.data) as EvalBaseline)
}
