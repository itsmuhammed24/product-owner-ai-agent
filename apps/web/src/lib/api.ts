/** Client API PO Agent — run, ingest, chat, export. */
import i18n from "@/lib/i18n"

const API_URL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '/api' : 'http://localhost:8000')

function formatApiError(body: { error?: string; detail?: string | unknown }, status: number, fallbackKey: string): string {
  const msg = body.error ?? (typeof body.detail === "string" ? body.detail : null)
  if (msg) return msg
  if (status === 429) return i18n.t("common.rateLimitError")
  if (status >= 500) return i18n.t("common.serverError")
  return i18n.t(fallbackKey)
}

export interface FeedbackItem {
  id: string
  source: string
  text: string
  client?: string
  segment?: string
  plan?: string
  created_at?: string
}

export interface PipelineResult {
  insights: Array<{
    request: string
    theme: string
    category: string
    occurrences: number
    evidence_quotes?: string[]
    source_feedback_ids: string[]
  }>
  backlog: Array<{
    feature: string
    theme: string
    moscow: string
    rice_score: number
    wsjf_score?: number
    impact?: number
    effort?: number
    reach?: number
    confidence?: number
    rationale: string
    source_feedback_ids: string[]
  }>
  stories: Array<{
    title: string
    user_story: string
    acceptance_criteria: string[]
    complexity: string
  } | null>
  roadmap: {
    Now: Array<{ feature: string }>
    Next: Array<{ feature: string }>
    Later: Array<{ feature: string }>
  }
  summary?: string
  errors?: string[]
  stories_before_critique?: Array<{
    title: string
    user_story: string
    acceptance_criteria: string[]
    complexity: string
  } | null>
}

export async function runPipeline(feedback: FeedbackItem[]): Promise<PipelineResult> {
  const res = await fetch(`${API_URL}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feedback }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { error?: string; detail?: string }
    throw new Error(formatApiError(err, res.status, "common.apiError"))
  }
  return res.json()
}

export type StreamStep = 'analyze' | 'insights' | 'backlog' | 'retrieval' | 'stories' | 'critique' | 'summary' | 'done' | 'error'

export async function runPipelineStream(
  feedback: FeedbackItem[],
  onStep: (step: StreamStep, data: Record<string, unknown>) => void
): Promise<PipelineResult> {
  const res = await fetch(`${API_URL}/run/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feedback }),
  })
  if (!res.ok) throw new Error(`${i18n.t("common.apiError")} ${res.status}`)
  const reader = res.body?.getReader()
  if (!reader) throw new Error('No response body')
  const decoder = new TextDecoder()
  let buffer = ''
  let result: PipelineResult | null = null
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n\n')
    buffer = lines.pop() || ''
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const obj = JSON.parse(line.slice(6)) as { step: string; [k: string]: unknown }
          const step = obj.step as StreamStep
          if (step === 'done') {
            const { step: _s, ...rest } = obj
            result = rest as unknown as PipelineResult
            onStep('done', obj)
          } else if (step === 'error') {
            throw new Error(String(obj.error))
          } else {
            onStep(step, obj)
          }
        } catch (e) {
          if (e instanceof SyntaxError) continue
          throw e
        }
      }
    }
  }
  if (!result) throw new Error('Stream ended without result')
  return result
}

export async function ingestFile(
  content: string,
  format: 'jsonl' | 'csv'
): Promise<{ feedback: FeedbackItem[]; count: number }> {
  const res = await fetch(`${API_URL}/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, format }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || err.error || `${i18n.t("common.ingestionError")} ${res.status}`)
  }
  return res.json()
}

export interface HealthStatus {
  ok: boolean
}

export async function checkHealth(): Promise<HealthStatus> {
  try {
    const res = await fetch(`${API_URL}/health`)
    return { ok: res.ok }
  } catch {
    return { ok: false }
  }
}

export async function ingestFromCanny(options?: {
  boardId?: string
  limit?: number
}): Promise<{ feedback: FeedbackItem[]; count: number }> {
  const res = await fetch(`${API_URL}/ingest/canny`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      board_id: options?.boardId ?? null,
      limit: options?.limit ?? 50,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || err.error || `${i18n.t("common.cannyError")} ${res.status}`)
  }
  return res.json()
}

export interface PartialResult {
  insights: PipelineResult['insights']
  backlog?: PipelineResult['backlog']
  roadmap?: PipelineResult['roadmap']
  analyzed_count?: number
  partial: boolean
  errors?: string[]
}

export async function runPartialPipeline(
  feedback: FeedbackItem[],
  stopAt: 'insights' | 'backlog'
): Promise<PartialResult> {
  const res = await fetch(`${API_URL}/run/partial`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feedback, stop_at: stopAt }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || err.error || `${i18n.t("common.apiError")} ${res.status}`)
  }
  return res.json()
}

export async function runWhatIf(
  backlog: PipelineResult['backlog'],
  itemIndex: number,
  overrides: { impact?: number; effort?: number; reach?: number; confidence?: number }
): Promise<{ backlog: PipelineResult['backlog']; roadmap: PipelineResult['roadmap'] }> {
  const res = await fetch(`${API_URL}/run/whatif`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ backlog, item_index: itemIndex, ...overrides }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.error || err.detail || `${i18n.t("common.whatIfError")} ${res.status}`)
  }
  return res.json()
}

export async function exportJiraCsv(stories: PipelineResult['stories']): Promise<Blob> {
  const res = await fetch(`${API_URL}/export/jira`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stories }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || err.error || `${i18n.t("common.exportError")} ${res.status}`)
  }
  return res.blob()
}

export interface ToolSuggestion {
  name: string
  params: Record<string, unknown>
  label: string
}

export async function sendChatMessage(
  message: string,
  context?: PipelineResult | null
): Promise<{ reply: string; toolSuggestion?: ToolSuggestion }> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, context: context ?? undefined }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { error?: string; detail?: string }
    throw new Error(formatApiError(err, res.status, "common.chatError"))
  }
  const data = (await res.json()) as { reply: string; tool_suggestion?: { name: string; params: Record<string, unknown>; label: string } }
  return {
    reply: data.reply,
    toolSuggestion: data.tool_suggestion ? { name: data.tool_suggestion.name, params: data.tool_suggestion.params, label: data.tool_suggestion.label } : undefined,
  }
}
