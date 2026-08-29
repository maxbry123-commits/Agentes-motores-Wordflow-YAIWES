export interface ReasoningTagScrubResult {
  visible: string
  reasoning: string
}

const TAG_NAMES = [
  'think',
  'thinking',
  'reasoning',
  'thought',
  'reasoning_scratchpad',
] as const

const OPEN_TAGS = TAG_NAMES.map((name) => `<${name}>`)
const CLOSE_TAGS = TAG_NAMES.map((name) => `</${name}>`)
const MAX_TAG_LENGTH = Math.max(...OPEN_TAGS.map((tag) => tag.length), ...CLOSE_TAGS.map((tag) => tag.length))

function isWhitespace(text: string): boolean {
  for (let i = 0; i < text.length; i++) {
    const code = text.charCodeAt(i)
    if (code !== 9 && code !== 10 && code !== 11 && code !== 12 && code !== 13 && code !== 32) return false
  }
  return true
}

function matchTagAt(lowerText: string, index: number, tags: string[]): number {
  for (const tag of tags) {
    if (lowerText.startsWith(tag, index)) return tag.length
  }
  return 0
}

function findFirstTag(text: string, tags: string[]): { index: number; length: number } {
  const lowerText = text.toLowerCase()
  let bestIndex = -1
  let bestLength = 0
  for (const tag of tags) {
    const index = lowerText.indexOf(tag)
    if (index !== -1 && (bestIndex === -1 || index < bestIndex)) {
      bestIndex = index
      bestLength = tag.length
    }
  }
  return { index: bestIndex, length: bestLength }
}

function maxPartialSuffix(text: string, tags: string[]): number {
  const lowerText = text.toLowerCase()
  const maxLength = Math.min(MAX_TAG_LENGTH - 1, lowerText.length)
  let best = 0
  for (let length = 1; length <= maxLength; length++) {
    const suffix = lowerText.slice(-length)
    if (tags.some((tag) => tag.startsWith(suffix))) best = length
  }
  return best
}

function stripOrphanCloseTags(text: string): string {
  const lowerText = text.toLowerCase()
  let output = ''
  let index = 0
  while (index < text.length) {
    const closeLength = matchTagAt(lowerText, index, CLOSE_TAGS)
    if (closeLength > 0) {
      index += closeLength
      while (index < text.length && isWhitespace(text[index])) index++
      continue
    }
    output += text[index]
    index++
  }
  return output
}

export class StreamingReasoningTagScrubber {
  private inBlock = false
  private buffer = ''
  private lastVisibleEndedNewline = true

  reset(): void {
    this.inBlock = false
    this.buffer = ''
    this.lastVisibleEndedNewline = true
  }

  feed(text: string): ReasoningTagScrubResult {
    if (!text) return { visible: '', reasoning: '' }
    let buffer = this.buffer + text
    this.buffer = ''
    let visible = ''
    let reasoning = ''

    while (buffer) {
      if (this.inBlock) {
        const close = findFirstTag(buffer, CLOSE_TAGS)
        if (close.index === -1) {
          const held = maxPartialSuffix(buffer, CLOSE_TAGS)
          const captureEnd = held ? buffer.length - held : buffer.length
          reasoning += buffer.slice(0, captureEnd)
          this.buffer = held ? buffer.slice(-held) : ''
          return { visible, reasoning }
        }
        reasoning += buffer.slice(0, close.index)
        buffer = buffer.slice(close.index + close.length)
        this.inBlock = false
        continue
      }

      const pair = this.findEarliestClosedPair(buffer)
      const open = this.findOpenAtBoundary(buffer)

      if (pair && (open.index === -1 || pair.start <= open.index)) {
        const preceding = stripOrphanCloseTags(buffer.slice(0, pair.start))
        if (preceding) {
          visible += preceding
          this.lastVisibleEndedNewline = preceding.endsWith('\n')
        }
        reasoning += buffer.slice(pair.contentStart, pair.contentEnd)
        buffer = buffer.slice(pair.end)
        continue
      }

      if (open.index !== -1) {
        const preceding = stripOrphanCloseTags(buffer.slice(0, open.index))
        if (preceding) {
          visible += preceding
          this.lastVisibleEndedNewline = preceding.endsWith('\n')
        }
        this.inBlock = true
        buffer = buffer.slice(open.index + open.length)
        continue
      }

      const held = Math.max(maxPartialSuffix(buffer, OPEN_TAGS), maxPartialSuffix(buffer, CLOSE_TAGS))
      const emitText = held ? buffer.slice(0, -held) : buffer
      this.buffer = held ? buffer.slice(-held) : ''
      if (emitText) {
        const cleaned = stripOrphanCloseTags(emitText)
        if (cleaned) {
          visible += cleaned
          this.lastVisibleEndedNewline = cleaned.endsWith('\n')
        }
      }
      return { visible, reasoning }
    }

    return { visible, reasoning }
  }

  flush(): ReasoningTagScrubResult {
    if (this.inBlock) {
      this.inBlock = false
      this.buffer = ''
      return { visible: '', reasoning: '' }
    }
    const tail = stripOrphanCloseTags(this.buffer)
    this.buffer = ''
    if (tail) this.lastVisibleEndedNewline = tail.endsWith('\n')
    return { visible: tail, reasoning: '' }
  }

  private findEarliestClosedPair(text: string): {
    start: number
    contentStart: number
    contentEnd: number
    end: number
  } | null {
    const lowerText = text.toLowerCase()
    let best: { start: number; contentStart: number; contentEnd: number; end: number } | null = null
    for (const name of TAG_NAMES) {
      const openTag = `<${name}>`
      const closeTag = `</${name}>`
      let searchFrom = 0
      while (searchFrom < lowerText.length) {
        const start = lowerText.indexOf(openTag, searchFrom)
        if (start === -1) break
        const contentStart = start + openTag.length
        const contentEnd = lowerText.indexOf(closeTag, contentStart)
        if (contentEnd !== -1) {
          const candidate = {
            start,
            contentStart,
            contentEnd,
            end: contentEnd + closeTag.length,
          }
          if (!best || candidate.start < best.start) best = candidate
          break
        }
        searchFrom = contentStart
      }
    }
    return best
  }

  private findOpenAtBoundary(text: string): { index: number; length: number } {
    const lowerText = text.toLowerCase()
    let best = { index: -1, length: 0 }
    for (const openTag of OPEN_TAGS) {
      let searchFrom = 0
      while (searchFrom < lowerText.length) {
        const index = lowerText.indexOf(openTag, searchFrom)
        if (index === -1) break
        if (this.isBlockBoundary(text.slice(0, index))) {
          if (best.index === -1 || index < best.index) best = { index, length: openTag.length }
          break
        }
        searchFrom = index + openTag.length
      }
    }
    return best
  }

  private isBlockBoundary(preceding: string): boolean {
    if (!preceding) return this.lastVisibleEndedNewline
    const lastNewline = Math.max(preceding.lastIndexOf('\n'), preceding.lastIndexOf('\r'))
    if (lastNewline !== -1) return isWhitespace(preceding.slice(lastNewline + 1))
    return this.lastVisibleEndedNewline && isWhitespace(preceding)
  }
}
