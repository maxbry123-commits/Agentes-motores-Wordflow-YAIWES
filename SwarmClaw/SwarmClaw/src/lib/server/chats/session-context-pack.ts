import { getContextStatus, type ContextStatus } from '@/lib/server/context-manager'
import type { BoardTask, Message, Session } from '@/types'

const SYSTEM_PROMPT_TOKEN_ESTIMATE = 2000
const DEFAULT_RECENT_MESSAGES = 12
const MAX_RECENT_MESSAGES = 40
const MAX_TEXT_CHARS = 900
const MAX_SMALL_TEXT_CHARS = 220
const MAX_ATTACHMENTS = 20

export type SessionContextPackStatus = 'ready' | 'attention' | 'blocked'

export interface SessionContextPackResumeHandle {
  kind: string
  id: string
  command: string
}

export interface SessionContextPackMessage {
  role: Message['role']
  time: number
  kind: Message['kind'] | null
  text: string
  attachmentCount: number
  toolCallNames: string[]
  sourceLabel: string | null
}

export interface SessionContextPackTask {
  id: string
  title: string
  status: BoardTask['status']
  agentId: string | null
  blockedBy: string[]
  blocks: string[]
  result: string | null
  error: string | null
  updatedAt: number | null
}

export interface SessionContextPackAttachment {
  path: string
  messageIndex: number
  role: Message['role']
  time: number
}

export interface SessionContextPack {
  schemaVersion: 1
  generatedAt: number
  status: SessionContextPackStatus
  session: {
    id: string
    name: string
    agentId: string | null
    provider: string
    model: string
    cwd: string
    projectId: string | null
    missionId: string | null
    tools: string[]
    extensions: string[]
  }
  connector: {
    platform: string | null
    connectorId: string | null
    scope: string | null
    threadId: string | null
    senderName: string | null
  }
  messageStats: {
    total: number
    visible: number
    hidden: number
    attachments: number
    toolEvents: number
    lastMessageAt: number | null
  }
  context: ContextStatus
  resumeHandles: SessionContextPackResumeHandle[]
  linkedTasks: SessionContextPackTask[]
  attachments: SessionContextPackAttachment[]
  runContext: {
    objective: string | null
    constraints: string[]
    keyFacts: string[]
    currentPlan: string[]
    completedSteps: string[]
    blockers: string[]
    updatedAt: number | null
  }
  recentMessages: SessionContextPackMessage[]
  nextActions: string[]
}

function compactText(value: unknown, maxChars = MAX_TEXT_CHARS): string {
  if (typeof value !== 'string') return ''
  const text = value.split(/\s+/).filter(Boolean).join(' ').trim()
  if (!text) return ''
  return text.length > maxChars ? `${text.slice(0, maxChars - 3)}...` : text
}

function compactList(values: unknown, maxItems = 8): string[] {
  if (!Array.isArray(values)) return []
  return values
    .map((item) => compactText(item, MAX_SMALL_TEXT_CHARS))
    .filter(Boolean)
    .slice(0, maxItems)
}

function sourceLabel(message: Message): string | null {
  const source = message.source
  if (!source) return null
  return source.connectorName || source.platform || source.connectorId || null
}

function isVisibleContextMessage(message: Message): boolean {
  if (message.suppressed || message.historyExcluded) return false
  if (message.kind === 'heartbeat' || message.kind === 'context-clear') return false
  return true
}

function messageAttachmentPaths(message: Message): string[] {
  const paths: string[] = []
  if (Array.isArray(message.attachedFiles)) {
    paths.push(...message.attachedFiles.filter((item): item is string => typeof item === 'string' && item.trim().length > 0))
  }
  if (typeof message.imagePath === 'string' && message.imagePath.trim()) paths.push(message.imagePath.trim())
  if (typeof message.imageUrl === 'string' && message.imageUrl.trim()) paths.push(message.imageUrl.trim())
  return Array.from(new Set(paths))
}

function buildRecentMessages(messages: Message[], maxRecentMessages: number): SessionContextPackMessage[] {
  return messages
    .filter(isVisibleContextMessage)
    .slice(-maxRecentMessages)
    .map((message) => ({
      role: message.role,
      time: message.time,
      kind: message.kind || null,
      text: compactText(message.text),
      attachmentCount: messageAttachmentPaths(message).length,
      toolCallNames: (message.toolEvents || [])
        .map((event) => compactText(event.name, 80))
        .filter(Boolean)
        .slice(0, 8),
      sourceLabel: sourceLabel(message),
    }))
}

function buildAttachments(messages: Message[]): SessionContextPackAttachment[] {
  const attachments: SessionContextPackAttachment[] = []
  messages.forEach((message, messageIndex) => {
    for (const path of messageAttachmentPaths(message)) {
      attachments.push({ path, messageIndex, role: message.role, time: message.time })
    }
  })
  return attachments.slice(-MAX_ATTACHMENTS)
}

function resumeHandles(session: Session): SessionContextPackResumeHandle[] {
  const handles: SessionContextPackResumeHandle[] = []
  const push = (kind: string, id: unknown, command: (value: string) => string) => {
    if (typeof id !== 'string' || !id.trim()) return
    const value = id.trim()
    handles.push({ kind, id: value, command: command(value) })
  }
  push('claude', session.claudeSessionId, (id) => `claude --resume ${id}`)
  push('codex', session.codexThreadId, (id) => `codex exec resume ${id}`)
  push('opencode', session.opencodeSessionId, (id) => `opencode run "<task>" --session ${id}`)
  push('gemini', session.geminiSessionId, (id) => `gemini --resume ${id} --prompt "<task>"`)
  push('copilot', session.copilotSessionId, (id) => `copilot -p "<task>" --resume ${id}`)
  push('droid', session.droidSessionId, (id) => `droid exec "<task>" --resume ${id}`)
  push('cursor', session.cursorSessionId, (id) => `cursor-agent --resume ${id} --print "<task>"`)
  push('qwen', session.qwenSessionId, (id) => `qwen --resume ${id} -p "<task>"`)

  const delegate = session.delegateResumeIds || {}
  push('claude-delegate', delegate.claudeCode, (id) => `claude --resume ${id}`)
  push('codex-delegate', delegate.codex, (id) => `codex exec resume ${id}`)
  push('opencode-delegate', delegate.opencode, (id) => `opencode run "<task>" --session ${id}`)
  push('gemini-delegate', delegate.gemini, (id) => `gemini --resume ${id} --prompt "<task>"`)
  push('copilot-delegate', delegate.copilot, (id) => `copilot -p "<task>" --resume ${id}`)
  push('droid-delegate', delegate.droid, (id) => `droid exec "<task>" --resume ${id}`)
  push('cursor-delegate', delegate.cursor, (id) => `cursor-agent --resume ${id} --print "<task>"`)
  push('qwen-delegate', delegate.qwen, (id) => `qwen --resume ${id} -p "<task>"`)
  return handles
}

function linkedTasksForSession(session: Session, tasks: Record<string, BoardTask>): SessionContextPackTask[] {
  return Object.values(tasks)
    .filter((task) => task.sessionId === session.id || task.createdInSessionId === session.id)
    .sort((left, right) => (right.updatedAt || 0) - (left.updatedAt || 0))
    .slice(0, 8)
    .map((task) => ({
      id: task.id,
      title: task.title || task.id,
      status: task.status,
      agentId: task.agentId || null,
      blockedBy: Array.isArray(task.blockedBy) ? task.blockedBy.filter(Boolean) : [],
      blocks: Array.isArray(task.blocks) ? task.blocks.filter(Boolean) : [],
      result: compactText(task.result, MAX_SMALL_TEXT_CHARS) || null,
      error: compactText(task.error, MAX_SMALL_TEXT_CHARS) || null,
      updatedAt: typeof task.updatedAt === 'number' ? task.updatedAt : null,
    }))
}

function buildNextActions(input: {
  context: ContextStatus
  linkedTasks: SessionContextPackTask[]
  recentMessages: SessionContextPackMessage[]
  resumeHandles: SessionContextPackResumeHandle[]
  session: Session
}): string[] {
  const actions: string[] = []
  if (input.context.strategy === 'critical') {
    actions.push('Compact the chat or start a new context window before continuing long work.')
  } else if (input.context.strategy === 'warning') {
    actions.push('Consider compacting soon; the context window is approaching the reserve limit.')
  }
  if (input.linkedTasks.some((task) => task.blockedBy.length > 0 && task.status !== 'completed')) {
    actions.push('Resolve the blocked linked task before handing this session to another operator.')
  }
  if (input.linkedTasks.some((task) => task.status === 'failed' || task.status === 'cancelled')) {
    actions.push('Review failed or cancelled linked tasks before resuming the session.')
  }
  if (input.resumeHandles.length > 0) {
    actions.push('Use a resume handle if continuing work in the matching CLI backend.')
  }
  if (!input.session.agentId) {
    actions.push('Link an agent when this context needs durable memory, tools, or scheduled follow-up.')
  }
  if (input.recentMessages.length === 0) {
    actions.push('Add the current objective before handing off; no visible recent turns are available.')
  }
  if (actions.length === 0) actions.push('Share this context pack with the next operator or agent before switching execution paths.')
  return Array.from(new Set(actions)).slice(0, 8)
}

function statusFrom(context: ContextStatus, linkedTasks: SessionContextPackTask[], recentMessages: SessionContextPackMessage[]): SessionContextPackStatus {
  if (context.strategy === 'critical') return 'blocked'
  if (linkedTasks.some((task) => task.status === 'failed' || task.status === 'cancelled')) return 'blocked'
  if (context.strategy === 'warning') return 'attention'
  if (linkedTasks.some((task) => task.blockedBy.length > 0 && task.status !== 'completed')) return 'attention'
  if (recentMessages.length === 0) return 'attention'
  return 'ready'
}

export function buildSessionContextPack(input: {
  session: Session
  messages: Message[]
  tasks?: Record<string, BoardTask>
  now?: number
  maxRecentMessages?: number
}): SessionContextPack {
  const now = input.now ?? Date.now()
  const maxRecentMessages = Math.max(1, Math.min(MAX_RECENT_MESSAGES, Math.trunc(input.maxRecentMessages || DEFAULT_RECENT_MESSAGES)))
  const messages = Array.isArray(input.messages) ? input.messages : []
  const context = getContextStatus(messages, SYSTEM_PROMPT_TOKEN_ESTIMATE, String(input.session.provider || ''), String(input.session.model || ''))
  const recentMessages = buildRecentMessages(messages, maxRecentMessages)
  const attachments = buildAttachments(messages)
  const linkedTasks = linkedTasksForSession(input.session, input.tasks || {})
  const handles = resumeHandles(input.session)
  const hidden = messages.filter((message) => !isVisibleContextMessage(message)).length
  const toolEvents = messages.reduce((sum, message) => sum + (message.toolEvents?.length || 0), 0)
  const nextActions = buildNextActions({ context, linkedTasks, recentMessages, resumeHandles: handles, session: input.session })

  return {
    schemaVersion: 1,
    generatedAt: now,
    status: statusFrom(context, linkedTasks, recentMessages),
    session: {
      id: input.session.id,
      name: input.session.name || input.session.id,
      agentId: input.session.agentId || null,
      provider: String(input.session.provider || ''),
      model: String(input.session.model || ''),
      cwd: input.session.cwd || '',
      projectId: input.session.projectId || null,
      missionId: input.session.missionId || null,
      tools: Array.isArray(input.session.tools) ? input.session.tools.filter(Boolean) : [],
      extensions: Array.isArray(input.session.extensions) ? input.session.extensions.filter(Boolean) : [],
    },
    connector: {
      platform: input.session.connectorContext?.platform || null,
      connectorId: input.session.connectorContext?.connectorId || null,
      scope: input.session.connectorContext?.scope || null,
      threadId: input.session.connectorContext?.threadId || null,
      senderName: input.session.connectorContext?.senderName || null,
    },
    messageStats: {
      total: messages.length,
      visible: messages.length - hidden,
      hidden,
      attachments: attachments.length,
      toolEvents,
      lastMessageAt: messages.at(-1)?.time || null,
    },
    context,
    resumeHandles: handles,
    linkedTasks,
    attachments,
    runContext: {
      objective: compactText(input.session.runContext?.objective, MAX_SMALL_TEXT_CHARS) || null,
      constraints: compactList(input.session.runContext?.constraints),
      keyFacts: compactList(input.session.runContext?.keyFacts),
      currentPlan: compactList(input.session.runContext?.currentPlan),
      completedSteps: compactList(input.session.runContext?.completedSteps),
      blockers: compactList(input.session.runContext?.blockers),
      updatedAt: input.session.runContext?.updatedAt || null,
    },
    recentMessages,
    nextActions,
  }
}

function iso(value: number | null | undefined): string {
  return typeof value === 'number' && Number.isFinite(value) ? new Date(value).toISOString() : 'n/a'
}

function bulletList(items: string[], empty: string): string[] {
  if (items.length === 0) return [`- ${empty}`]
  return items.map((item) => `- ${item}`)
}

export function formatSessionContextPackMarkdown(pack: SessionContextPack): string {
  const lines: string[] = []
  lines.push(`# Session Context Pack: ${pack.session.name}`)
  lines.push('')
  lines.push(`Generated: ${iso(pack.generatedAt)}`)
  lines.push(`Status: ${pack.status}`)
  lines.push(`Session: ${pack.session.id}`)
  lines.push(`Provider: ${pack.session.provider}${pack.session.model ? ` / ${pack.session.model}` : ''}`)
  lines.push(`Agent: ${pack.session.agentId || 'n/a'}`)
  lines.push(`Working directory: ${pack.session.cwd || 'n/a'}`)
  lines.push(`Messages: ${pack.messageStats.visible} visible / ${pack.messageStats.total} total`)
  lines.push(`Context: ${pack.context.percentUsed}% used, ${pack.context.remainingTokens.toLocaleString()} tokens remaining`)
  lines.push('')
  lines.push('## Next Actions')
  lines.push(...bulletList(pack.nextActions, 'No immediate action required.'))
  lines.push('')
  lines.push('## Run Context')
  lines.push(`Objective: ${pack.runContext.objective || 'n/a'}`)
  lines.push(...bulletList(pack.runContext.currentPlan.map((item) => `Plan: ${item}`), 'No current plan recorded.'))
  lines.push(...bulletList(pack.runContext.blockers.map((item) => `Blocker: ${item}`), 'No blockers recorded.'))
  lines.push('')
  lines.push('## Linked Tasks')
  if (pack.linkedTasks.length === 0) {
    lines.push('- No linked tasks.')
  } else {
    for (const task of pack.linkedTasks) {
      const blockers = task.blockedBy.length > 0 ? `, blocked by ${task.blockedBy.join(', ')}` : ''
      lines.push(`- ${task.id}: ${task.title} (${task.status}${blockers})`)
      if (task.result) lines.push(`  - Result: ${task.result}`)
      if (task.error) lines.push(`  - Error: ${task.error}`)
    }
  }
  lines.push('')
  lines.push('## Resume Handles')
  if (pack.resumeHandles.length === 0) {
    lines.push('- No external resume handles.')
  } else {
    for (const handle of pack.resumeHandles) lines.push(`- ${handle.kind}: \`${handle.command}\``)
  }
  lines.push('')
  lines.push('## Attachments')
  if (pack.attachments.length === 0) {
    lines.push('- No attachments in the visible pack window.')
  } else {
    for (const attachment of pack.attachments) {
      lines.push(`- ${attachment.path} (${attachment.role}, ${iso(attachment.time)})`)
    }
  }
  lines.push('')
  lines.push('## Recent Turns')
  if (pack.recentMessages.length === 0) {
    lines.push('- No visible recent turns.')
  } else {
    for (const message of pack.recentMessages) {
      const tools = message.toolCallNames.length > 0 ? ` Tools: ${message.toolCallNames.join(', ')}.` : ''
      const attachments = message.attachmentCount > 0 ? ` Attachments: ${message.attachmentCount}.` : ''
      const source = message.sourceLabel ? ` Source: ${message.sourceLabel}.` : ''
      lines.push(`- ${message.role} at ${iso(message.time)}:${source}${attachments}${tools} ${message.text || '[no text]'}`.trim())
    }
  }
  lines.push('')
  return lines.join('\n')
}
