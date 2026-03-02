import { useState, useRef, useEffect } from "react"
import { Upload, Loader2, FileJson, Sparkles, MessageSquare, CloudDownload, UserCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  runPipeline,
  runPipelineStream,
  runPartialPipeline,
  checkHealth,
  ingestFile,
  ingestFromCanny,
  type FeedbackItem,
  type PipelineResult,
  type StreamStep,
} from "@/lib/api"
import { loadSampleFeedbacks, loadMinimalFeedbacks } from "@/lib/sampleFeedback"
import { addRunStats } from "@/lib/stats"
import { useNavigate } from "react-router-dom"
import { AnimatedNumber } from "@/components/AnimatedNumber"
import { usePipelineResult } from "@/contexts/PipelineResultContext"
import { useTranslation } from "react-i18next"

export default function Feedback() {
  const { t } = useTranslation()
  const [file, setFile] = useState<File | null>(null)
  const [items, setItems] = useState<FeedbackItem[]>([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PipelineResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [health, setHealth] = useState<{ ok: boolean } | null>(null)
  const [cannyLoading, setCannyLoading] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  const { setResult: setContextResult } = usePipelineResult()

  const parseFile = async (f: File): Promise<FeedbackItem[]> => {
    const text = await f.text()
    const format = f.name.endsWith(".csv") ? "csv" : "jsonl"
    const { feedback } = await ingestFile(text, format)
    return feedback
  }

  const onFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    setError(null)
    setResult(null)
    try {
      const parsed = await parseFile(f)
      setItems(parsed)
      setFile(f)
    } catch (err) {
      const msg = err instanceof Error ? err.message : t("feedback.errors.unknown")
      setError(
        msg.includes("ingestion") || msg.includes("fetch")
          ? t("feedback.errors.apiUnreachable")
          : msg
      )
    }
  }

  const loadFromCanny = async () => {
    setCannyLoading(true)
    setError(null)
    try {
      const { feedback: fb } = await ingestFromCanny({ limit: 50 })
      setItems(fb)
      setFile(null)
      setResult(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : t("feedback.errors.canny"))
    } finally {
      setCannyLoading(false)
    }
  }

  const loadSample = async () => {
    try {
      const parsed = await loadSampleFeedbacks(Infinity)
      setItems(parsed)
      setFile(null)
      setError(null)
      setResult(null)
    } catch {
      setError(t("feedback.errors.sampleUnavailable"))
    }
  }

  const loadMinimal = async () => {
    try {
      const parsed = await loadMinimalFeedbacks()
      setItems(parsed)
      setFile(null)
      setError(null)
      setResult(null)
    } catch {
      setError(t("feedback.errors.sampleUnavailable"))
    }
  }

  const [streamStep, setStreamStep] = useState<StreamStep>("analyze")

  const run = async () => {
    if (items.length === 0) return
    setLoading(true)
    setError(null)
    setStreamStep("analyze")
    try {
      let data: PipelineResult
      try {
        data = await runPipelineStream(items, (step) => setStreamStep(step))
      } catch {
        setStreamStep("analyze")
        data = await runPipeline(items)
      }
      addRunStats(
        items.length,
        data.backlog?.length ?? 0,
        (data.stories ?? []).filter(Boolean).length
      )
      setResult(data)
      setContextResult(data)
      navigate("/roadmap", { state: { result: data } })
    } catch (err) {
      setError(err instanceof Error ? err.message : t("feedback.errors.api"))
    } finally {
      setLoading(false)
    }
  }

  const checkApi = async () => {
    const h = await checkHealth()
    setHealth({ ok: h.ok })
  }

  useEffect(() => {
    checkHealth().then((h) => setHealth({ ok: h.ok }))
  }, [])

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b bg-gradient-to-b from-[hsl(340_100%_27%_/0.02)] to-transparent px-8 pt-8 pb-6">
        <h1 className="font-serif text-3xl font-bold tracking-tight text-foreground">
          {t("feedback.title")}
        </h1>
        <p className="mt-2 text-muted-foreground">
          {t("feedback.subtitleShort")}
        </p>
        {items.length > 0 && (
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-[hsl(340_100%_27%_/0.06)] px-4 py-2 w-fit">
            <MessageSquare className="h-5 w-5 text-primary" />
            <span className="font-serif text-2xl font-bold text-primary">
              <AnimatedNumber value={items.length} />
            </span>
            <span className="text-sm text-muted-foreground">
              {t("feedback.feedbacksLoaded")}
            </span>
          </div>
        )}
      </div>

      <div className="space-y-6 p-8">
        <Card className="thiga-card border-0">
          <CardHeader>
            <CardTitle className="font-serif">{t("feedback.loadData")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-4">
              <input
                ref={fileRef}
                type="file"
                accept=".jsonl,.csv"
                className="hidden"
                onChange={onFileChange}
              />
              <Button variant="outline" onClick={() => fileRef.current?.click()}>
                <Upload className="mr-2 h-4 w-4" />
                {t("feedback.uploadFile")}
              </Button>
              <Button variant="outline" onClick={loadSample}>
                <FileJson className="mr-2 h-4 w-4" />
                {t("feedback.loadSample")}
              </Button>
              <Button variant="outline" onClick={loadMinimal}>
                <FileJson className="mr-2 h-4 w-4" />
                {t("feedback.loadMinimal")}
              </Button>
              <Button
                variant="outline"
                onClick={loadFromCanny}
                disabled={cannyLoading}
              >
                {cannyLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <CloudDownload className="mr-2 h-4 w-4" />
                )}
                {t("feedback.importCanny")}
              </Button>
              <Button variant="ghost" size="sm" onClick={checkApi}>
                {t("feedback.checkApi")}
              </Button>
            </div>
            {health !== null && (
              <p className="text-sm">
                {t("feedback.apiStatus", { status: health.ok ? t("feedback.apiOk") : t("feedback.apiUnreachable") })}
              </p>
            )}
            {file && <p className="text-sm text-muted-foreground">{file.name}</p>}
            {items.length > 0 && (
              <Badge variant="secondary" className="text-base px-3 py-1">
                {t("feedback.itemsCount", { count: items.length })}
              </Badge>
            )}
          </CardContent>
        </Card>

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            {error}
          </div>
        )}

        {loading && (
          <Card className="thiga-card border-0">
            <CardContent className="flex items-center gap-4 py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" aria-hidden />
              <span>{t(`feedback.steps.${streamStep}`)}</span>
            </CardContent>
          </Card>
        )}

        {items.length > 0 && !loading && (
          <Card className="thiga-card border-0">
            <CardContent className="pt-6 space-y-4">
              <div className="flex flex-wrap gap-3">
                <Button onClick={run} size="lg" className="btn-thiga">
                  <Sparkles className="mr-2 h-4 w-4" />
                  {t("feedback.runAnalysis")}
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={async () => {
                    setLoading(true)
                    setError(null)
                    try {
                      const partial = await runPartialPipeline(items, "insights")
                      const toNav: Partial<PipelineResult> & { partial?: boolean } = {
                        insights: partial.insights,
                        backlog: [],
                        roadmap: { Now: [], Next: [], Later: [] },
                        stories: [],
                        partial: true,
                      }
                      setContextResult(toNav as PipelineResult)
                      navigate("/roadmap", { state: { result: toNav, partialStep: "insights", feedbackForContinue: items } })
                    } catch (err) {
                      setError(err instanceof Error ? err.message : t("feedback.errors.api"))
                    } finally {
                      setLoading(false)
                    }
                  }}
                >
                  <UserCheck className="mr-2 h-4 w-4" />
                  {t("feedback.reviewAfterInsights")}
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={async () => {
                    setLoading(true)
                    setError(null)
                    try {
                      const partial = await runPartialPipeline(items, "backlog")
                      const toNav: Partial<PipelineResult> & { partial?: boolean } = {
                        insights: partial.insights,
                        backlog: partial.backlog ?? [],
                        roadmap: partial.roadmap ?? { Now: [], Next: [], Later: [] },
                        stories: [],
                        partial: true,
                      }
                      setContextResult(toNav as PipelineResult)
                      navigate("/roadmap", { state: { result: toNav, partialStep: "backlog", feedbackForContinue: items } })
                    } catch (err) {
                      setError(err instanceof Error ? err.message : t("feedback.errors.api"))
                    } finally {
                      setLoading(false)
                    }
                  }}
                >
                  <UserCheck className="mr-2 h-4 w-4" />
                  {t("feedback.reviewAfterBacklog")}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                {t("feedback.humanInTheLoop")}
              </p>
            </CardContent>
          </Card>
        )}

        {items.length === 0 && !loading && (
          <Card className="thiga-card border-0 border-primary/20">
            <CardHeader>
              <CardTitle className="font-serif">{t("feedback.demoOneClick")}</CardTitle>
              <p className="text-sm text-muted-foreground">{t("feedback.demoDescription")}</p>
            </CardHeader>
            <CardContent>
              <Button
                variant="default"
                size="lg"
                className="btn-thiga"
                onClick={async () => {
                  setError(null)
                  try {
                    const sample = await loadSampleFeedbacks(8)
                    setItems(sample)
                    setLoading(true)
                    setStreamStep("analyze")
                    try {
                      let data: PipelineResult
                      try {
                        data = await runPipelineStream(sample, (step) => setStreamStep(step))
                      } catch {
                        data = await runPipeline(sample)
                      }
                      addRunStats(
                        sample.length,
                        data.backlog?.length ?? 0,
                        (data.stories ?? []).filter(Boolean).length
                      )
                      setResult(data)
                      setContextResult(data)
                      navigate("/roadmap", { state: { result: data } })
                    } finally {
                      setLoading(false)
                    }
                  } catch (err) {
                    setError(err instanceof Error ? err.message : t("feedback.errors.demo"))
                  }
                }}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                {t("feedback.demoOneClick")}
              </Button>
            </CardContent>
          </Card>
        )}

        {result && (
          <Button variant="outline" onClick={() => navigate("/roadmap")}>
            {t("feedback.viewResults")}
          </Button>
        )}
      </div>
    </div>
  )
}
