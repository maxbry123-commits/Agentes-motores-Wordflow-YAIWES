import assert from 'node:assert/strict'
import { test } from 'node:test'
import { StreamingReasoningTagScrubber } from './reasoning-tag-scrubber'
import { ChatTurnState } from './chat-turn-state'
import { processIterationEvents } from './iteration-event-handler'

function drive(deltas: string[]) {
  const scrubber = new StreamingReasoningTagScrubber()
  let visible = ''
  let reasoning = ''
  for (const delta of deltas) {
    const result = scrubber.feed(delta)
    visible += result.visible
    reasoning += result.reasoning
  }
  const final = scrubber.flush()
  visible += final.visible
  reasoning += final.reasoning
  return { visible, reasoning }
}

test('strips closed reasoning pairs from visible text and captures reasoning', () => {
  assert.deepEqual(
    drive(['Hello <think>private note</think> world']),
    { visible: 'Hello  world', reasoning: 'private note' },
  )
})

test('handles all supported tag variants case-insensitively', () => {
  assert.deepEqual(
    drive(['<THINKING>a</Thinking><reasoning>b</reasoning><thought>c</thought><REASONING_SCRATCHPAD>d</REASONING_SCRATCHPAD>done']),
    { visible: 'done', reasoning: 'abcd' },
  )
})

test('holds split opening tags across stream deltas', () => {
  assert.deepEqual(
    drive(['<', 'think>reasoning</think>', 'done']),
    { visible: 'done', reasoning: 'reasoning' },
  )
})

test('captures reasoning until a split close tag resolves', () => {
  assert.deepEqual(
    drive(['<think>first', ' second</th', 'ink>answer']),
    { visible: 'answer', reasoning: 'first second' },
  )
})

test('does not treat a mid-line prose mention as an open reasoning block', () => {
  const text = 'Use the <think> element for examples'
  assert.deepEqual(drive([text]), { visible: text, reasoning: '' })
})

test('does strip a bounded mid-line pair because it is model reasoning markup', () => {
  assert.deepEqual(
    drive(['Use <think>hidden</think>this answer']),
    { visible: 'Use this answer', reasoning: 'hidden' },
  )
})

test('drops unterminated reasoning content at flush after capturing streamed content', () => {
  assert.deepEqual(
    drive(['Visible\n<think>private reasoning with no close']),
    { visible: 'Visible\n', reasoning: 'private reasoning with no close' },
  )
})

test('reset clears an interrupted reasoning block and buffered partial tags', () => {
  const scrubber = new StreamingReasoningTagScrubber()
  assert.deepEqual(scrubber.feed('<think>hanging'), { visible: '', reasoning: 'hanging' })
  scrubber.reset()
  assert.deepEqual(scrubber.feed('fresh<'), { visible: 'fresh', reasoning: '' })
  scrubber.reset()
  assert.deepEqual(scrubber.feed('content'), { visible: 'content', reasoning: '' })
})

test('processIterationEvents routes split reasoning tags away from visible deltas', async () => {
  async function* eventStream() {
    yield { event: 'on_chat_model_stream', data: { chunk: { content: '<' } } }
    yield { event: 'on_chat_model_stream', data: { chunk: { content: 'think>private' } } }
    yield { event: 'on_chat_model_stream', data: { chunk: { content: ' reasoning</th' } } }
    yield { event: 'on_chat_model_stream', data: { chunk: { content: 'ink>done' } } }
  }

  const state = new ChatTurnState()
  const writes: string[] = []
  const outcome = await processIterationEvents({
    eventStream: eventStream(),
    state,
    timers: {
      armIdleWatchdog: () => undefined,
      clearIdleWatchdog: () => undefined,
      clearRequiredToolKickoff: () => undefined,
    } as never,
    loopTracker: {} as never,
    toolEventTracker: {} as never,
    session: { id: 'sess_reasoning_tags', provider: 'openai', model: 'gpt-4o-mini' } as never,
    message: 'answer briefly',
    write: (data: string) => writes.push(data),
    sessionExtensions: [],
    boundedExternalExecutionTask: false,
    toolToExtensionMap: {},
    iterationController: new AbortController(),
  })

  assert.equal(outcome.iterationText, 'done')
  assert.equal(state.fullText, 'done')
  assert.equal(state.accumulatedThinking, 'private reasoning')

  const rendered = writes.join('')
  assert.match(rendered, /"t":"thinking"/)
  assert.match(rendered, /"text":"private"/)
  assert.match(rendered, /"text":" reasoning"/)
  assert.doesNotMatch(rendered, /"t":"d"[^\n]*private/)
  assert.doesNotMatch(rendered, /<think>|<\/think>/i)
})
