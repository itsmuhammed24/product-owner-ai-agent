import { useState, useRef, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Target, Send, Loader2, X, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { sendChatMessage, type ToolSuggestion } from "@/lib/api"
import { usePipelineResult } from "@/contexts/PipelineResultContext"
import { useTranslation } from "react-i18next"

type Message = {
  role: "user" | "assistant"
  content: string
  toolSuggestion?: ToolSuggestion
}

const PROMPT_KEYS_WITH_CONTEXT = ["synthèse", "summarizeInsights", "quickWins", "whyPrioritized", "openWhatif"] as const
const PROMPT_KEYS_NO_CONTEXT = ["howToStart", "whatIsPOAgent"] as const

export default function ChatFab() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const { result } = usePipelineResult()
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    listRef.current?.scrollTo(0, listRef.current.scrollHeight)
  }, [messages])

  function executeTool(tool: ToolSuggestion) {
    const { name, params } = tool
    if (name === "navigate_whatif") {
      navigate("/roadmap", { state: { result, initialTab: "backlog" } })
      setOpen(false)
    } else if (name === "navigate_roadmap") {
      navigate("/roadmap", { state: { result, initialTab: "roadmap" } })
      setOpen(false)
    } else if (name === "navigate_explainability") {
      navigate("/roadmap", { state: { result, initialTab: "explainability" } })
      setOpen(false)
    } else if (name === "run_partial_insights" || name === "run_partial_backlog") {
      navigate("/feedback")
      setOpen(false)
    } else if (name === "search_backlog" && result?.backlog && params?.query) {
      const q = String(params.query).toLowerCase()
      const matches = result.backlog.filter(
        (b) =>
          (b.feature ?? "").toLowerCase().includes(q) ||
          (b.theme ?? "").toLowerCase().includes(q)
      )
      const summary =
        matches.length > 0
          ? matches.slice(0, 5).map((m) => `• ${m.feature} (RICE: ${m.rice_score})`).join("\n")
          : t("chat.noResults")
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Résultats pour « ${params.query} » :\n${summary}` },
      ])
    }
  }

  const send = async (textOverride?: string) => {
    const text = (textOverride ?? input).trim()
    if (!text || loading) return

    if (!textOverride) setInput("")
    setMessages((m) => [...m, { role: "user", content: text }])
    setLoading(true)

    try {
      const { reply, toolSuggestion } = await sendChatMessage(text, result)
      setMessages((m) => [...m, { role: "assistant", content: reply, toolSuggestion }])
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: err instanceof Error ? err.message : t("chat.sendError"),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full shadow-lg transition-all hover:scale-105 hover:shadow-xl"
        style={{
          background: "var(--gradient-primary)",
          color: "white",
        }}
        aria-label={t("chat.openAssistant")}
      >
        <Target className="h-6 w-6" />
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex justify-end bg-black/20 backdrop-blur-sm"
          onClick={() => setOpen(false)}
        >
          <div
            className="flex h-full w-full max-w-md flex-col bg-background shadow-xl sm:rounded-l-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div
              className="flex items-center justify-between border-b px-4 py-3"
              style={{ borderColor: "hsl(var(--border))" }}
            >
              <div className="flex items-center gap-2">
                <img src="/thiga-logo.png" alt="" className="h-8 w-8 rounded-lg object-contain" />
                <div>
                  <p className="font-serif font-semibold">{t("sidebar.appName")}</p>
                  <p className="text-xs text-muted-foreground">
                    {result ? t("chat.itemsInContext", { count: result.backlog?.length ?? 0 }) : t("chat.noAnalysis")}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setOpen(false)}
                aria-label={t("chat.close")}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div
              ref={listRef}
              className="flex-1 overflow-y-auto p-4 space-y-4"
            >
              {messages.length === 0 && (
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    {t("chat.howCanIHelp")}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {(result ? PROMPT_KEYS_WITH_CONTEXT : PROMPT_KEYS_NO_CONTEXT).map((key, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => send(t(`chat.prompts.${key}`))}
                        className="rounded-full border px-3 py-1.5 text-left text-xs transition-colors hover:border-primary/50 hover:bg-primary/5"
                        style={{ borderColor: "hsl(var(--border))" }}
                      >
                        {t(`chat.prompts.${key}`)}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {result ? t("chat.orPasteFeedback") : t("chat.noContextHint")}
                  </p>
                </div>
              )}
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] px-4 py-2.5 text-sm ${
                      msg.role === "user"
                        ? "rounded-lg rounded-br-sm text-primary-foreground"
                        : "rounded-lg rounded-bl-sm border-l-2 border-primary/30 bg-muted/50 pl-4"
                    }`}
                    style={
                      msg.role === "user"
                        ? { background: "hsl(340 100% 27%)" }
                        : {}
                    }
                  >
                    <p className="whitespace-pre-wrap">
                      {msg.content.split(/(\*\*[^*]+\*\*)/g).map((part, j) =>
                        part.startsWith("**") && part.endsWith("**") ? (
                          <strong key={j}>{part.slice(2, -2)}</strong>
                        ) : (
                          part
                        )
                      )}
                    </p>
                    {msg.role === "assistant" && msg.toolSuggestion && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="mt-2 gap-1.5 text-xs"
                        onClick={() => executeTool(msg.toolSuggestion!)}
                      >
                        <ExternalLink className="h-3 w-3" />
                        {msg.toolSuggestion.label}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="flex items-center gap-2 rounded-lg rounded-bl-sm border-l-2 border-primary/30 bg-muted/50 px-4 py-2.5">
                    <Loader2 className="h-4 w-4 animate-spin text-primary" />
                    <span className="text-sm text-muted-foreground">
                      {t("chat.thinking")}
                    </span>
                  </div>
                </div>
              )}
            </div>

            <div
              className="border-t p-4"
              style={{ borderColor: "hsl(var(--border))" }}
            >
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
                  placeholder={t("chat.placeholder")}
                  className="flex-1 rounded-lg border bg-background px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary/20"
                  style={{ borderColor: "hsl(var(--border))" }}
                  disabled={loading}
                />
                <Button
                  onClick={() => send()}
                  disabled={!input.trim() || loading}
                  className="btn-thiga shrink-0 px-4"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
