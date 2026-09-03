const DEFAULT_LM_STUDIO_ENDPOINT = 'http://127.0.0.1:1234/v1'

const OPENAI_COMPATIBLE_ENDPOINT_SUFFIXES = [
  '/chat/completions',
  '/responses',
  '/models',
  '/completions',
  '/embeddings',
]

function clean(value: string | null | undefined): string {
  return typeof value === 'string' ? value.trim() : ''
}

function trimTrailingSlashes(value: string): string {
  let output = value
  while (output.endsWith('/') && output.length > 1) output = output.slice(0, -1)
  return output
}

function toUrl(value: string): URL | null {
  const trimmed = clean(value)
  if (!trimmed) return null
  try {
    return new URL(trimmed)
  } catch {
    try {
      return new URL(`http://${trimmed}`)
    } catch {
      return null
    }
  }
}

function stripKnownEndpointPath(pathname: string): string {
  let path = trimTrailingSlashes(pathname || '/')
  const lower = path.toLowerCase()
  for (const suffix of OPENAI_COMPATIBLE_ENDPOINT_SUFFIXES) {
    if (lower === suffix || lower.endsWith(suffix)) {
      path = path.slice(0, path.length - suffix.length)
      break
    }
  }
  path = trimTrailingSlashes(path)
  return path || '/'
}

export function normalizeOpenAiCompatibleV1Endpoint(
  input: string | null | undefined,
  fallback = DEFAULT_LM_STUDIO_ENDPOINT,
): string {
  const parsed = toUrl(clean(input) || fallback) || toUrl(fallback)
  if (!parsed) return trimTrailingSlashes(clean(input) || fallback)

  const cleanedPath = stripKnownEndpointPath(parsed.pathname)
  parsed.pathname = cleanedPath.toLowerCase().endsWith('/v1')
    ? cleanedPath
    : `${cleanedPath === '/' ? '' : cleanedPath}/v1`
  parsed.search = ''
  parsed.hash = ''
  return trimTrailingSlashes(parsed.toString())
}

export function normalizeLmStudioEndpoint(input?: string | null): string {
  return normalizeOpenAiCompatibleV1Endpoint(input, DEFAULT_LM_STUDIO_ENDPOINT)
}

