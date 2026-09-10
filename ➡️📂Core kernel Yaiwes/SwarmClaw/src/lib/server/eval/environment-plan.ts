import fs from 'node:fs'
import path from 'node:path'

import { WORKSPACE_DIR } from '@/lib/server/data-dir'
import { resolveAgentRouteCandidatesWithProfiles, type ResolvedAgentRoute } from '@/lib/server/agents/agent-runtime-config'
import { checkCliProviderReady, type CliProviderReadyResult } from '@/lib/server/cli-provider-readiness'
import { listOpenClawGatewayEnvironments } from '@/lib/server/gateways/gateway-topology'
import { loadAgents, loadCredentials } from '@/lib/server/storage'
import { isCliProviderId } from '@/lib/providers/cli-provider-metadata'
import type { Agent, GatewayProfile, OpenClawEnvironmentSummary, OpenClawGatewayEnvironmentList } from '@/types'
import type {
  EvalEnvironmentCheck,
  EvalEnvironmentGeneratedFile,
  EvalEnvironmentPlan,
  EvalEnvironmentTarget,
  EvalScenario,
  EvalScenarioFixture,
} from './types'
import { getScenario, getSuiteScenarios } from './scenarios'
import { listOpenClawGatewayProfiles } from '../gateways/gateway-profile-service'

export interface EvalEnvironmentPlanInput {
  agentId: string
  scenarioId?: string | null
  suite?: string | null
  gatewayProfileId?: string | null
  environmentId?: string | null
  refreshGateway?: boolean
}

interface EvalEnvironmentPlanDeps {
  now?: () => number
  loadAgents?: () => Record<string, Agent>
  loadCredentials?: () => Record<string, unknown>
  listGatewayProfiles?: () => GatewayProfile[]
  listGatewayEnvironments?: (id: string) => Promise<OpenClawGatewayEnvironmentList | null>
  checkCliProviderReady?: (providerId: string) => CliProviderReadyResult
}

interface WriteEvalWorkspaceOptions {
  runId: string
  workspacePath: string
  scenario: EvalScenario
  plan: EvalEnvironmentPlan
}

function normalizeOptionalId(value: string | null | undefined): string | null {
  return typeof value === 'string' && value.trim() ? value.trim() : null
}

function uniqueStrings(values: string[]): string[] {
  return [...new Set(values.map((value) => value.trim()).filter(Boolean))]
    .sort((left, right) => left.localeCompare(right))
}

function scenarioSet(input: EvalEnvironmentPlanInput): { scenarios: EvalScenario[]; missing?: string } {
  const scenarioId = normalizeOptionalId(input.scenarioId)
  if (scenarioId) {
    const scenario = getScenario(scenarioId)
    return scenario ? { scenarios: [scenario] } : { scenarios: [], missing: scenarioId }
  }
  const suite = normalizeOptionalId(input.suite) || 'core'
  return { scenarios: getSuiteScenarios(suite) }
}

function maxScore(scenarios: EvalScenario[]): number {
  return scenarios.reduce(
    (sum, scenario) => sum + scenario.scoringCriteria.reduce((criterionSum, criterion) => criterionSum + criterion.weight, 0),
    0,
  )
}

function timeoutMs(scenarios: EvalScenario[]): number {
  return scenarios.reduce((sum, scenario) => sum + scenario.timeoutMs, 0)
}

function fixtureFiles(scenarios: EvalScenario[]): EvalEnvironmentGeneratedFile[] {
  return scenarios.flatMap((scenario) => (scenario.fixtures || []).map((fixture) => ({
    path: fixture.path,
    kind: 'fixture' as const,
    required: true,
  })))
}

function baseGeneratedFiles(scenarios: EvalScenario[]): EvalEnvironmentGeneratedFile[] {
  return [
    { path: 'README.md', kind: 'readme', required: true },
    { path: 'environment.json', kind: 'manifest', required: true },
    { path: '.env.swarmclaw-eval', kind: 'env', required: true },
    ...fixtureFiles(scenarios),
  ]
}

function providerNeedsCredential(route: ResolvedAgentRoute): boolean {
  if (route.provider === 'openclaw') return false
  if (route.provider === 'ollama' && route.ollamaMode !== 'cloud') return false
  if (isCliProviderId(route.provider)) return false
  return true
}

function credentialExists(credentialId: string | null | undefined, credentials: Record<string, unknown>): boolean {
  return typeof credentialId === 'string' && credentialId.trim() ? Boolean(credentials[credentialId]) : false
}

function checkLevelRank(level: EvalEnvironmentCheck['level']): number {
  if (level === 'error') return 2
  if (level === 'warn') return 1
  return 0
}

function statusFromChecks(checks: EvalEnvironmentCheck[]): EvalEnvironmentPlan['status'] {
  const max = checks.reduce((rank, check) => Math.max(rank, checkLevelRank(check.level)), 0)
  if (max >= 2) return 'blocked'
  if (max >= 1) return 'warning'
  return 'ready'
}

function pickGatewayProfile(
  route: ResolvedAgentRoute | null,
  profiles: GatewayProfile[],
  requestedProfileId: string | null,
): GatewayProfile | null {
  if (requestedProfileId) {
    return profiles.find((profile) => profile.id === requestedProfileId) || null
  }
  if (route?.gatewayProfileId) {
    return profiles.find((profile) => profile.id === route.gatewayProfileId) || null
  }
  return profiles.find((profile) => profile.isDefault) || profiles[0] || null
}

function summarizeGatewayTarget(route: ResolvedAgentRoute, profile: GatewayProfile | null): EvalEnvironmentTarget {
  return {
    kind: 'gateway',
    provider: route.provider,
    model: route.model,
    label: profile?.name || route.label,
    gatewayProfileId: profile?.id || route.gatewayProfileId || null,
    capabilities: ['agent.run', 'sessions', 'tools', 'workspace'],
    refreshedAt: profile?.stats?.lastTopologyCheckedAt || profile?.lastCheckedAt || null,
  }
}

function summarizeLocalTarget(route: ResolvedAgentRoute): EvalEnvironmentTarget {
  return {
    kind: 'local',
    provider: route.provider,
    model: route.model,
    label: route.label,
    capabilities: ['agent.run', 'tools', 'workspace'],
    refreshedAt: null,
  }
}

function addEnvHint(
  hints: EvalEnvironmentPlan['envHints'],
  key: string,
  value: string | null | undefined,
  description?: string,
): void {
  if (!value) return
  hints.push({ key, value, ...(description ? { description } : {}) })
}

function buildEnvHints(params: {
  agent: Agent | null
  scenarios: EvalScenario[]
  suite: string | null
  target: EvalEnvironmentTarget | null
}): EvalEnvironmentPlan['envHints'] {
  const hints: EvalEnvironmentPlan['envHints'] = []
  addEnvHint(hints, 'SWARMCLAW_EVAL_AGENT_ID', params.agent?.id, 'Agent under validation')
  addEnvHint(hints, 'SWARMCLAW_EVAL_AGENT_NAME', params.agent?.name, 'Agent display name')
  addEnvHint(hints, 'SWARMCLAW_EVAL_SCENARIOS', params.scenarios.map((scenario) => scenario.id).join(','), 'Comma-separated eval scenario ids')
  addEnvHint(hints, 'SWARMCLAW_EVAL_SUITE', params.suite, 'Eval suite name')
  addEnvHint(hints, 'SWARMCLAW_EVAL_TARGET_KIND', params.target?.kind, 'Resolved execution target kind')
  addEnvHint(hints, 'SWARMCLAW_EVAL_PROVIDER', params.target?.provider, 'Resolved provider')
  addEnvHint(hints, 'SWARMCLAW_EVAL_MODEL', params.target?.model, 'Resolved model')
  addEnvHint(hints, 'SWARMCLAW_EVAL_GATEWAY_PROFILE_ID', params.target?.gatewayProfileId || null, 'Resolved gateway profile id')
  addEnvHint(hints, 'SWARMCLAW_EVAL_ENVIRONMENT_ID', params.target?.environmentId || null, 'Requested or selected gateway environment id')
  return hints
}

function normalizeEnvironmentCapabilities(environment: OpenClawEnvironmentSummary | null | undefined): string[] {
  return uniqueStrings(environment?.capabilities || [])
}

async function attachGatewayEnvironment(
  target: EvalEnvironmentTarget,
  profile: GatewayProfile | null,
  checks: EvalEnvironmentCheck[],
  input: EvalEnvironmentPlanInput,
  deps: Required<Pick<EvalEnvironmentPlanDeps, 'listGatewayEnvironments'>>,
): Promise<EvalEnvironmentTarget> {
  if (!profile) return target
  const requestedEnvironmentId = normalizeOptionalId(input.environmentId)

  if (profile.status === 'offline') {
    checks.push({
      code: 'gateway_offline',
      level: 'error',
      message: `${profile.name} is offline.`,
      hint: 'Refresh or repair the gateway before running evals through it.',
    })
  } else if (profile.status === 'degraded') {
    checks.push({
      code: 'gateway_degraded',
      level: 'warn',
      message: `${profile.name} is degraded.`,
      detail: profile.lastError || undefined,
    })
  } else if (profile.status === 'pending' || profile.status === 'unknown') {
    checks.push({
      code: 'gateway_unverified',
      level: 'warn',
      message: `${profile.name} has not reported a healthy gateway status yet.`,
    })
  }

  const environmentCount = profile.stats?.environmentCount || 0
  const availableEnvironmentCount = profile.stats?.availableEnvironmentCount || 0
  if (environmentCount > 0 && availableEnvironmentCount === 0) {
    checks.push({
      code: 'no_available_gateway_environment',
      level: 'error',
      message: `${profile.name} has ${environmentCount} execution environment${environmentCount === 1 ? '' : 's'}, but none are available.`,
    })
  }

  if (!input.refreshGateway) {
    if (requestedEnvironmentId) {
      checks.push({
        code: 'environment_not_refreshed',
        level: 'warn',
        message: `Environment ${requestedEnvironmentId} was requested but not refreshed.`,
        hint: 'Run validation with refresh enabled to verify the exact environment.',
      })
      return { ...target, environmentId: requestedEnvironmentId }
    }
    checks.push({
      code: 'gateway_snapshot_only',
      level: 'info',
      message: 'Using the last stored gateway topology snapshot for validation.',
    })
    return target
  }

  const snapshot = await deps.listGatewayEnvironments(profile.id)
  if (!snapshot) {
    checks.push({
      code: 'gateway_environment_snapshot_missing',
      level: 'error',
      message: `${profile.name} could not be refreshed for environment validation.`,
    })
    return target
  }
  for (const error of snapshot.errors) {
    checks.push({
      code: 'gateway_environment_refresh_error',
      level: 'warn',
      message: `${error.method}: ${error.message}`,
    })
  }
  const environments = snapshot.environments
  const selected = requestedEnvironmentId
    ? environments.find((environment) => environment.id === requestedEnvironmentId) || null
    : environments.find((environment) => environment.status === 'available') || environments[0] || null
  if (requestedEnvironmentId && !selected) {
    checks.push({
      code: 'environment_not_found',
      level: 'error',
      message: `Requested execution environment ${requestedEnvironmentId} was not found on ${profile.name}.`,
    })
    return { ...target, environmentId: requestedEnvironmentId, refreshedAt: snapshot.refreshedAt }
  }
  if (!selected) {
    checks.push({
      code: 'no_gateway_environments',
      level: 'warn',
      message: `${profile.name} did not report any execution environments.`,
    })
    return { ...target, refreshedAt: snapshot.refreshedAt }
  }
  if (selected.status !== 'available') {
    checks.push({
      code: 'environment_unavailable',
      level: selected.status === 'error' ? 'error' : 'warn',
      message: `${selected.label || selected.id} is ${selected.status}.`,
    })
  } else {
    checks.push({
      code: 'environment_available',
      level: 'info',
      message: `${selected.label || selected.id} is available for validation runs.`,
    })
  }
  return {
    ...target,
    environmentId: selected.id,
    environmentLabel: selected.label || selected.id,
    environmentStatus: selected.status,
    capabilities: normalizeEnvironmentCapabilities(selected),
    refreshedAt: snapshot.refreshedAt,
  }
}

export async function buildEvalEnvironmentPlan(
  input: EvalEnvironmentPlanInput,
  deps: EvalEnvironmentPlanDeps = {},
): Promise<EvalEnvironmentPlan> {
  const now = deps.now || (() => Date.now())
  const generatedAt = now()
  const loadAgentsImpl = deps.loadAgents || (() => loadAgents() as Record<string, Agent>)
  const loadCredentialsImpl = deps.loadCredentials || (() => loadCredentials() as Record<string, unknown>)
  const listGatewayProfilesImpl = deps.listGatewayProfiles || listOpenClawGatewayProfiles
  const checkCliProviderReadyImpl = deps.checkCliProviderReady || checkCliProviderReady
  const checks: EvalEnvironmentCheck[] = []
  const { scenarios, missing } = scenarioSet(input)
  const suite = normalizeOptionalId(input.suite) || (input.scenarioId ? null : 'core')
  const agents = loadAgentsImpl()
  const agent = agents[input.agentId] || null
  const requiredTools = uniqueStrings(scenarios.flatMap((scenario) => scenario.tools || []))
  let target: EvalEnvironmentTarget | null = null

  if (missing) {
    checks.push({
      code: 'scenario_not_found',
      level: 'error',
      message: `Eval scenario ${missing} was not found.`,
    })
  } else if (scenarios.length === 0) {
    checks.push({
      code: 'scenario_set_empty',
      level: 'error',
      message: 'No eval scenarios matched the requested suite.',
    })
  }

  if (!agent) {
    checks.push({
      code: 'agent_not_found',
      level: 'error',
      message: `Agent ${input.agentId} was not found.`,
    })
  } else {
    if (agent.trashedAt) {
      checks.push({ code: 'agent_trashed', level: 'error', message: `${agent.name} is in trash.` })
    }
    if (agent.disabled) {
      checks.push({ code: 'agent_disabled', level: 'error', message: `${agent.name} is disabled.` })
    }

    const gatewayProfiles = listGatewayProfilesImpl()
    const [route] = resolveAgentRouteCandidatesWithProfiles(agent, gatewayProfiles)
    if (!route) {
      checks.push({
        code: 'route_unresolved',
        level: 'error',
        message: `${agent.name} does not have a runnable provider/model route.`,
      })
    } else if (route.provider === 'openclaw') {
      const profile = pickGatewayProfile(route, gatewayProfiles, normalizeOptionalId(input.gatewayProfileId))
      if (!profile) {
        checks.push({
          code: 'gateway_profile_missing',
          level: 'error',
          message: 'No gateway profile is available for this agent route.',
        })
        target = summarizeGatewayTarget(route, null)
      } else {
        target = await attachGatewayEnvironment(
          summarizeGatewayTarget(route, profile),
          profile,
          checks,
          input,
          { listGatewayEnvironments: deps.listGatewayEnvironments || listOpenClawGatewayEnvironments },
        )
      }
    } else {
      target = summarizeLocalTarget(route)
      if (isCliProviderId(route.provider)) {
        const ready = checkCliProviderReadyImpl(route.provider)
        checks.push({
          code: ready.ok ? 'cli_provider_ready' : 'cli_provider_not_ready',
          level: ready.ok ? 'info' : 'error',
          message: ready.message,
          detail: ready.binaryPath,
        })
      } else if (providerNeedsCredential(route) && !credentialExists(route.credentialId, loadCredentialsImpl())) {
        checks.push({
          code: 'credential_missing',
          level: 'warn',
          message: `${route.provider} does not have a stored credential for this route.`,
          hint: 'The run may still work if the provider is configured through environment variables.',
        })
      }
    }
  }

  if (requiredTools.length > 0) {
    checks.push({
      code: 'tools_declared',
      level: 'info',
      message: `${requiredTools.length} eval tool${requiredTools.length === 1 ? '' : 's'} will be enabled: ${requiredTools.join(', ')}.`,
    })
  } else {
    checks.push({
      code: 'no_tools_required',
      level: 'info',
      message: 'This eval scenario does not require tool access.',
    })
  }

  const envHints = buildEnvHints({ agent, scenarios, suite, target })

  return {
    generatedAt,
    status: statusFromChecks(checks),
    agentId: input.agentId,
    agentName: agent?.name || input.agentId,
    scenarioIds: scenarios.map((scenario) => scenario.id),
    suite,
    target,
    checks,
    requiredTools,
    missingTools: [],
    maxScore: maxScore(scenarios),
    timeoutMs: timeoutMs(scenarios),
    generatedFiles: baseGeneratedFiles(scenarios),
    envHints,
  }
}

function safeFixtureDestination(workspacePath: string, fixture: EvalScenarioFixture): string {
  const relative = fixture.path.trim()
  if (!relative || path.isAbsolute(relative)) {
    throw new Error(`Unsafe eval fixture path: ${fixture.path}`)
  }
  const destination = path.resolve(workspacePath, relative)
  const root = path.resolve(workspacePath)
  if (destination !== root && !destination.startsWith(`${root}${path.sep}`)) {
    throw new Error(`Unsafe eval fixture path: ${fixture.path}`)
  }
  return destination
}

function writeTextFile(filePath: string, content: string, mode?: number): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true })
  fs.writeFileSync(filePath, content.endsWith('\n') ? content : `${content}\n`, { encoding: 'utf8', mode })
}

function envLine(hint: EvalEnvironmentPlan['envHints'][number]): string {
  return `${hint.key}=${JSON.stringify(hint.value)}`
}

export function writeEvalEnvironmentWorkspace(options: WriteEvalWorkspaceOptions): EvalEnvironmentGeneratedFile[] {
  const { runId, workspacePath, scenario, plan } = options
  fs.mkdirSync(workspacePath, { recursive: true })

  const readme = [
    `# Eval Workspace: ${scenario.name}`,
    '',
    `Run ID: ${runId}`,
    `Agent: ${plan.agentName} (${plan.agentId})`,
    `Scenario: ${scenario.id}`,
    `Status at start: ${plan.status}`,
    '',
    'Runtime manifest: ./environment.json',
    'Environment hints: ./.env.swarmclaw-eval',
    '',
    'This directory is isolated for eval artifacts, fixtures, and generated outputs.',
  ].join('\n')
  writeTextFile(path.join(workspacePath, 'README.md'), readme)
  writeTextFile(path.join(workspacePath, 'environment.json'), JSON.stringify({ runId, plan }, null, 2))
  writeTextFile(
    path.join(workspacePath, '.env.swarmclaw-eval'),
    [
      '# Generated by SwarmClaw. Contains eval context only, not secrets.',
      `SWARMCLAW_EVAL_RUN_ID=${JSON.stringify(runId)}`,
      ...plan.envHints.map(envLine),
    ].join('\n'),
  )

  for (const fixture of scenario.fixtures || []) {
    writeTextFile(safeFixtureDestination(workspacePath, fixture), fixture.content, fixture.mode)
  }

  return [
    { path: 'README.md', kind: 'readme', required: true },
    { path: 'environment.json', kind: 'manifest', required: true },
    { path: '.env.swarmclaw-eval', kind: 'env', required: true },
    ...fixtureFiles([scenario]),
  ]
}

export function resolveEvalWorkspacePath(runId: string): string {
  return path.join(WORKSPACE_DIR, 'evals', runId)
}
