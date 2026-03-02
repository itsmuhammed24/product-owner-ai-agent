import { useState, useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BarChart3, Target, ArrowRight, MessageSquare, ListOrdered, Presentation, Minus, RefreshCw, Sparkles, Info } from "lucide-react"
import type { PipelineResult, FeedbackItem } from "@/lib/api"
import { runWhatIf, runPipeline } from "@/lib/api"
import { AnimatedNumber } from "@/components/AnimatedNumber"
import { usePipelineResult } from "@/contexts/PipelineResultContext"
import { usePresentation } from "@/contexts/PresentationContext"
import WordCloud from "@/components/WordCloud"
import ExportReport from "@/components/ExportReport"
import { formatRiceScore } from "@/lib/utils"
import { useTranslation } from "react-i18next"

export default function Roadmap() {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const { setResult: setContextResult } = usePipelineResult()
  const [whatIfLoading, setWhatIfLoading] = useState(false)
  const [whatIfError, setWhatIfError] = useState<string | null>(null)
  const [whatIfIdx, setWhatIfIdx] = useState(0)
  const [whatIfImpact, setWhatIfImpact] = useState(2)
  const [whatIfEffort, setWhatIfEffort] = useState(4)
  const { isPresentation, setPresentation } = usePresentation()
  const [result, setResult] = useState<PipelineResult | null>(
    location.state?.result ?? null
  )
  const [continueLoading, setContinueLoading] = useState(false)
  const feedbackForContinue = location.state?.feedbackForContinue as FeedbackItem[] | undefined
  const isPartial = (result as { partial?: boolean })?.partial === true

  useEffect(() => {
    if (!result && location.state?.result) {
      setResult(location.state.result)
    }
  }, [location.state, result])

  useEffect(() => {
    if (result) setContextResult(result)
  }, [result, setContextResult])

  const roadmap = result?.roadmap ?? { Now: [], Next: [], Later: [] }
  const insights = result?.insights ?? []
  const backlog = result?.backlog ?? []

  useEffect(() => {
    if (backlog.length > 0) {
      const b = backlog[Math.min(whatIfIdx, backlog.length - 1)] ?? backlog[0]
      setWhatIfImpact(b.impact ?? 2)
      setWhatIfEffort(b.effort ?? 4)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [whatIfIdx, backlog.length])

  function riceToLabel(rice: number): string {
    if (rice >= 75) return t("roadmap.riceLabels.quickWin")
    if (rice >= 50) return t("roadmap.riceLabels.strategic")
    return t("roadmap.riceLabels.postpone")
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="flex items-center justify-between border-b bg-gradient-to-b from-[hsl(340_100%_27%_/0.02)] to-transparent px-8 pt-8 pb-6">
        <div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-foreground">
            {t("roadmap.title")}
          </h1>
          <p className="mt-1 text-muted-foreground">
            {t("roadmap.subtitle")}
          </p>
        {result?.summary && (
          <div className="mt-4 rounded-lg border border-primary/20 bg-[hsl(340_100%_27%_/0.04)] px-4 py-3">
            <p className="text-xs font-medium uppercase tracking-wider text-primary/80">{t("roadmap.summary")}</p>
            <p className="mt-1 text-sm text-foreground">{result.summary}</p>
          </div>
        )}
        {result && (
          <div className="mt-4 flex flex-wrap gap-4">
            <div className="flex items-center gap-2 rounded-lg bg-[hsl(340_100%_27%_/0.06)] px-3 py-1.5">
              <MessageSquare className="h-4 w-4 text-primary" />
              <span className="font-serif font-bold text-primary">
                <AnimatedNumber value={insights.length} />
              </span>
              <span className="text-xs text-muted-foreground">{t("roadmap.insights")}</span>
            </div>
            <div className="flex items-center gap-2 rounded-lg bg-[hsl(340_100%_27%_/0.06)] px-3 py-1.5">
              <ListOrdered className="h-4 w-4 text-primary" />
              <span className="font-serif font-bold text-primary">
                <AnimatedNumber value={backlog.length} />
              </span>
              <span className="text-xs text-muted-foreground">{t("roadmap.backlog")}</span>
            </div>
          </div>
        )}
        </div>
        <div className="flex flex-wrap gap-2">
          {result && (
            <>
              <ExportReport result={result} />
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPresentation(!isPresentation)}
                className="border-primary/30 text-primary hover:bg-primary/5"
              >
                {isPresentation ? <Minus className="mr-1.5 h-4 w-4" /> : <Presentation className="mr-1.5 h-4 w-4" />}
                {isPresentation ? t("roadmap.quitPresentation") : t("roadmap.presentation")}
              </Button>
            </>
          )}
          {isPartial && feedbackForContinue && feedbackForContinue.length > 0 && (
            <Button
              className="btn-thiga"
              disabled={continueLoading}
              onClick={async () => {
                setContinueLoading(true)
                try {
                  const full = await runPipeline(feedbackForContinue)
                  setResult(full)
                  setContextResult(full)
                } finally {
                  setContinueLoading(false)
                }
              }}
            >
              {continueLoading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
              {t("roadmap.continueToStories")}
            </Button>
          )}
          <Button
            variant="outline"
            onClick={() => navigate("/feedback")}
            className="border-primary/30 text-primary hover:bg-primary/5"
          >
            {t("roadmap.newAnalysis")}
          </Button>
        </div>
      </div>

      <div className="p-8">
      {!result ? (
        <Card className="thiga-card border-0">
          <CardContent className="py-12 text-center text-muted-foreground">
            <BarChart3 className="mx-auto mb-4 h-12 w-12 opacity-50" />
            <p>{t("roadmap.runAnalysisFromFeedback")}</p>
            <Button className="btn-thiga mt-4" onClick={() => navigate("/feedback")}>
              {t("roadmap.analyzeFeedbacks")}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Tabs
          key={location.state?.initialTab ?? "roadmap"}
          defaultValue={location.state?.initialTab ?? "roadmap"}
          className="space-y-6"
        >
          <TabsList className="grid w-full max-w-2xl grid-cols-4">
            <TabsTrigger value="roadmap">{t("roadmap.tabs.roadmap")}</TabsTrigger>
            <TabsTrigger value="insights">{t("roadmap.tabs.insights")}</TabsTrigger>
            <TabsTrigger value="backlog">{t("roadmap.tabs.backlog")}</TabsTrigger>
            <TabsTrigger value="explainability">
              <Info className="mr-1.5 h-4 w-4" />
              {t("roadmap.tabs.explainability")}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="roadmap">
            <div className="grid gap-6 md:grid-cols-3">
              <Card className="thiga-card border-0">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-red-600">
                    <Target className="h-5 w-5" />
                    {t("roadmap.nowMust")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {roadmap.Now.length
                      ? roadmap.Now.map((b, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <ArrowRight className="mt-0.5 h-4 w-4 shrink-0" />
                            {b.feature}
                          </li>
                        ))
                      : "—"}
                  </ul>
                </CardContent>
              </Card>
              <Card className="thiga-card border-0">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-amber-600">
                    {t("roadmap.nextShould")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {roadmap.Next.length
                      ? roadmap.Next.map((b, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <ArrowRight className="mt-0.5 h-4 w-4 shrink-0" />
                            {b.feature}
                          </li>
                        ))
                      : "—"}
                  </ul>
                </CardContent>
              </Card>
              <Card className="thiga-card border-0">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-600">
                    {t("roadmap.laterCould")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {roadmap.Later.length
                      ? roadmap.Later.map((b, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <ArrowRight className="mt-0.5 h-4 w-4 shrink-0" />
                            {b.feature}
                          </li>
                        ))
                      : "—"}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="insights">
            {insights.length > 0 && (
              <div className="mb-6 rounded-xl border p-4" style={{ borderColor: "hsl(var(--border))" }}>
                <p className="mb-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  {t("roadmap.keyThemes")}
                </p>
                <WordCloud insights={insights} />
              </div>
            )}
            <div className="space-y-4">
              {insights.map((ins, i) => (
                <Card key={i} className="thiga-card border-0">
                  <CardHeader>
                    <CardTitle className="text-base">{ins.request}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      {ins.theme} • {t("roadmap.occurrences", { count: ins.occurrences })}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="backlog">
            {backlog.length > 0 && (
              <Card className="thiga-card border-0 mb-6">
                <CardHeader>
                  <CardTitle className="text-base">{t("roadmap.whatIf")}</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {t("roadmap.whatIfDesc")}
                  </p>
                </CardHeader>
                <CardContent className="flex flex-wrap items-end gap-4">
                  <div className="flex-1 min-w-[200px]">
                    <label htmlFor="whatif-item" className="text-xs font-medium text-muted-foreground">{t("roadmap.item")}</label>
                    <select
                      id="whatif-item"
                      className="mt-1 block w-full rounded-md border bg-background px-3 py-2 text-sm"
                      value={whatIfIdx}
                      onChange={(e) => {
                        const idx = parseInt(e.target.value, 10)
                        setWhatIfIdx(idx)
                        const b = backlog[idx]
                        if (b) {
                          setWhatIfImpact(b.impact ?? 2)
                          setWhatIfEffort(b.effort ?? 4)
                        }
                      }}
                    >
                      {backlog.map((b, i) => (
                        <option key={i} value={i}>{i + 1}. {b.feature}</option>
                      ))}
                    </select>
                  </div>
                  <div className="w-36">
                    <label htmlFor="whatif-impact" className="text-xs font-medium text-muted-foreground">{t("roadmap.impactLabel", { value: whatIfImpact.toFixed(1) })}</label>
                    <input
                      id="whatif-impact"
                      type="range"
                      min="1"
                      max="3"
                      step="0.1"
                      value={whatIfImpact}
                      onChange={(e) => setWhatIfImpact(parseFloat(e.target.value))}
                      className="mt-1 block w-full"
                    />
                  </div>
                  <div className="w-36">
                    <label htmlFor="whatif-effort" className="text-xs font-medium text-muted-foreground">{t("roadmap.effortLabel", { value: whatIfEffort.toFixed(1) })}</label>
                    <input
                      id="whatif-effort"
                      type="range"
                      min="1"
                      max="10"
                      step="0.5"
                      value={whatIfEffort}
                      onChange={(e) => setWhatIfEffort(parseFloat(e.target.value))}
                      className="mt-1 block w-full"
                    />
                  </div>
                  <Button
                    size="sm"
                    disabled={whatIfLoading}
                    onClick={async () => {
                      if (!result) return
                      setWhatIfLoading(true)
                      setWhatIfError(null)
                      try {
                        const data = await runWhatIf(result.backlog, whatIfIdx, { impact: whatIfImpact, effort: whatIfEffort })
                        const newResult = { ...result, backlog: data.backlog, roadmap: data.roadmap }
                        setResult(newResult)
                        setContextResult(newResult)
                      } catch (err) {
                        setWhatIfError(err instanceof Error ? err.message : t("common.whatIfError"))
                      } finally {
                        setWhatIfLoading(false)
                      }
                    }}
                  >
                    {whatIfLoading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                    {t("roadmap.recalculate")}
                  </Button>
                  {whatIfError && (
                    <p className="mt-2 text-sm text-destructive">{whatIfError}</p>
                  )}
                </CardContent>
              </Card>
            )}
            <div className="space-y-4">
              {backlog.map((b, i) => {
                const label = riceToLabel(b.rice_score)
                return (
                  <Card key={i} className="thiga-card border-0">
                    <CardHeader>
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <CardTitle className="text-base">#{i + 1} {b.feature}</CardTitle>
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                            label === "Quick Win"
                              ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                              : label === "Stratégique"
                              ? "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400"
                              : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                          }`}
                        >
                          {label}
                        </span>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm font-medium">
                        {t("roadmap.scoreRice")} : <span className="text-primary">{formatRiceScore(b.rice_score ?? 0)}</span>
                        {b.wsjf_score != null && b.wsjf_score > 0 && (
                          <> | {t("roadmap.scoreWsjf")}: {b.wsjf_score} </>
                        )}
                        {" | "}{b.moscow}
                      </p>
                      <p className="mt-2 text-sm text-muted-foreground">
                        {b.rationale}
                      </p>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>

          <TabsContent value="explainability" className="space-y-4">
            <p className="text-sm text-muted-foreground">
              {t("roadmap.traceability")}
            </p>
            {backlog.length > 0 ? (
              backlog.map((b, i) => (
                <Card key={i} className="thiga-card border-0">
                  <CardHeader>
                    <CardTitle className="text-base">{b.feature}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <p>
                      <span className="font-medium text-muted-foreground">{t("roadmap.scoreRice")} :</span> {b.rice_score?.toFixed(2) ?? "—"}
                      {" | "}
                      <span className="font-medium text-muted-foreground">{t("roadmap.scoreWsjf")} :</span> {b.wsjf_score ?? "—"}
                      {" | "}
                      <span className="font-medium text-muted-foreground">MoSCoW :</span> {b.moscow}
                    </p>
                    <p>
                      <span className="font-medium text-muted-foreground">Evidence IDs :</span>{" "}
                      {(b.source_feedback_ids ?? []).join(", ") || "—"}
                    </p>
                    <p>
                      <span className="font-medium text-muted-foreground">Rationale :</span> {b.rationale}
                    </p>
                  </CardContent>
                </Card>
              ))
            ) : (
              <p className="text-muted-foreground">{t("roadmap.noBacklogToExplain")}</p>
            )}
          </TabsContent>
        </Tabs>
      )}

      {result && !isPartial && (
        <div className="mt-8">
          <Button
            onClick={() => navigate("/stories", { state: { result } })}
            className="btn-thiga"
          >
            {t("roadmap.viewStories")}
          </Button>
        </div>
      )}
      </div>
    </div>
  )
}
