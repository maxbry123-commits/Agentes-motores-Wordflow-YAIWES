import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import test from 'node:test'

import type { Agent, GatewayProfile } from '@/types'
import { getScenario } from './scenarios'
import { buildEvalEnvironmentPlan, writeEvalEnvironmentWorkspace } from './environment-plan'
import type { EvalEnvironmentPlan, EvalScenario } from './types'

function makeAgent(overrides: Partial<Agent> = {}): Agent {
  return {
    id: 'agent-1',
    name: 'Eval Agent',
    description: 'Validates eval environments.',
    systemPrompt: 'You are an eval agent.',
    provider: 'ollama',
    model: 'llama3',
    ollamaMode: 'local',
    tools: [],
    createdAt: 1,
    updatedAt: 1,
    ...overrides,
  } as Agent
}

function makeGateway(overrides: Partial<GatewayProfile> = {}): GatewayProfile {
  return {
    id: 'gateway-1',
    name: 'Gateway 1',
    provider: 'openclaw',
    endpoint: 'http://127.0.0.1:18789/v1',
    wsUrl: 'ws://127.0.0.1:18789',
    credentialId: null,
    status: 'healthy',
    stats: {
      nodeCount: 1,
      connectedNodeCount: 1,
      environmentCount: 1,
      availableEnvironmentCount: 1,
      pendingNodePairings: 0,
      pendingDevicePairings: 0,
      pairedDeviceCount: 0,
      lastTopologyCheckedAt: 2,
      lastTopologyErrorCount: 0,
      lastTopologyError: null,
    },
    createdAt: 1,
    updatedAt: 1,
    ...overrides,
  } as GatewayProfile
}

test('eval environment plan blocks missing CLI provider readiness before a run spends tokens', async () => {
  const plan = await buildEvalEnvironmentPlan(
    { agentId: 'agent-cli', scenarioId: 'coding-prime' },
    {
      now: () => 123,
      loadAgents: () => ({
        'agent-cli': makeAgent({
          id: 'agent-cli',
          provider: 'codex-cli',
          model: 'gpt-5.2',
          ollamaMode: null,
        }),
      }),
      listGatewayProfiles: () => [],
      checkCliProviderReady: () => ({
        ok: false,
        message: 'Codex CLI is not installed.',
        providerId: 'codex-cli',
        displayName: 'Codex CLI',
        binaryName: 'codex',
      }),
    },
  )

  assert.equal(plan.status, 'blocked')
  assert.equal(plan.target?.kind, 'local')
  assert.ok(plan.checks.some((check) => check.code === 'cli_provider_not_ready' && check.level === 'error'))
})

test('eval environment plan refreshes gateway environments and selects an available target', async () => {
  const plan = await buildEvalEnvironmentPlan(
    {
      agentId: 'agent-openclaw',
      scenarioId: 'coding-prime',
      refreshGateway: true,
    },
    {
      now: () => 456,
      loadAgents: () => ({
        'agent-openclaw': makeAgent({
          id: 'agent-openclaw',
          provider: 'openclaw',
          model: 'default',
          gatewayProfileId: 'gateway-1',
        }),
      }),
      listGatewayProfiles: () => [makeGateway()],
      listGatewayEnvironments: async () => ({
        profile: makeGateway(),
        connected: true,
        refreshedAt: 789,
        errors: [],
        environments: [
          { id: 'env-busy', type: 'sandbox', label: 'Busy', status: 'starting', capabilities: ['agent.run'] },
          { id: 'env-ready', type: 'sandbox', label: 'Ready', status: 'available', capabilities: ['agent.run', 'workspace'] },
        ],
      }),
    },
  )

  assert.equal(plan.status, 'ready')
  assert.equal(plan.target?.kind, 'gateway')
  assert.equal(plan.target?.environmentId, 'env-ready')
  assert.equal(plan.target?.environmentStatus, 'available')
  assert.deepEqual(plan.target?.capabilities, ['agent.run', 'workspace'])
  assert.ok(plan.checks.some((check) => check.code === 'environment_available'))
})

test('eval environment plan blocks gateways with no available execution environments', async () => {
  const plan = await buildEvalEnvironmentPlan(
    { agentId: 'agent-openclaw', scenarioId: 'coding-prime' },
    {
      loadAgents: () => ({
        'agent-openclaw': makeAgent({
          id: 'agent-openclaw',
          provider: 'openclaw',
          model: 'default',
          gatewayProfileId: 'gateway-1',
        }),
      }),
      listGatewayProfiles: () => [
        makeGateway({
          stats: {
            nodeCount: 1,
            connectedNodeCount: 1,
            environmentCount: 2,
            availableEnvironmentCount: 0,
            pendingNodePairings: 0,
            pendingDevicePairings: 0,
            pairedDeviceCount: 0,
          },
        }),
      ],
    },
  )

  assert.equal(plan.status, 'blocked')
  assert.ok(plan.checks.some((check) => check.code === 'no_available_gateway_environment'))
})

test('eval workspace writer materializes manifests, env hints, and scenario fixtures', async () => {
  const scenario = getScenario('multi-step-analyze')
  assert.ok(scenario)
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'swarmclaw-eval-env-'))
  const plan = await buildEvalEnvironmentPlan(
    { agentId: 'agent-1', scenarioId: scenario.id },
    {
      now: () => 999,
      loadAgents: () => ({ 'agent-1': makeAgent() }),
      listGatewayProfiles: () => [],
    },
  )

  const files = writeEvalEnvironmentWorkspace({
    runId: 'run-1',
    workspacePath: root,
    scenario,
    plan,
  })

  assert.ok(files.some((file) => file.path === 'package.json' && file.kind === 'fixture'))
  assert.ok(fs.existsSync(path.join(root, 'README.md')))
  assert.ok(fs.existsSync(path.join(root, 'environment.json')))
  assert.ok(fs.existsSync(path.join(root, '.env.swarmclaw-eval')))
  const fixture = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8')) as { dependencies?: Record<string, string> }
  assert.equal(fixture.dependencies?.zod, '^4.1.13')
  assert.ok(fs.readFileSync(path.join(root, '.env.swarmclaw-eval'), 'utf8').includes('SWARMCLAW_EVAL_RUN_ID="run-1"'))
})

test('eval workspace writer refuses fixture paths outside the eval workspace', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'swarmclaw-eval-unsafe-'))
  const scenario: EvalScenario = {
    id: 'unsafe-fixture',
    name: 'Unsafe Fixture',
    category: 'coding',
    description: 'Unsafe fixture path test',
    userMessage: 'noop',
    expectedBehaviors: [],
    scoringCriteria: [],
    timeoutMs: 1,
    tools: [],
    fixtures: [{ path: '../outside.txt', content: 'nope' }],
  }
  const plan: EvalEnvironmentPlan = {
    generatedAt: 1,
    status: 'ready',
    agentId: 'agent-1',
    agentName: 'Eval Agent',
    scenarioIds: [scenario.id],
    suite: null,
    target: null,
    checks: [],
    requiredTools: [],
    missingTools: [],
    maxScore: 0,
    timeoutMs: 1,
    generatedFiles: [],
    envHints: [],
  }

  assert.throws(() => writeEvalEnvironmentWorkspace({
    runId: 'run-unsafe',
    workspacePath: root,
    scenario,
    plan,
  }), /Unsafe eval fixture path/)
})
