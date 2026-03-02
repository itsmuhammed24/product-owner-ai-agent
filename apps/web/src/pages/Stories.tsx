import { useState, useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { FileText, Download, Presentation, Minus, GitCompare } from "lucide-react"
import type { PipelineResult } from "@/lib/api"
import { AnimatedNumber } from "@/components/AnimatedNumber"
import { usePipelineResult } from "@/contexts/PipelineResultContext"
import { usePresentation } from "@/contexts/PresentationContext"
import ExportReport from "@/components/ExportReport"
import { useTranslation } from "react-i18next"

export default function Stories() {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const { setResult: setContextResult } = usePipelineResult()
  const { isPresentation, setPresentation } = usePresentation()
  const [result, setResult] = useState<PipelineResult | null>(
    location.state?.result ?? null
  )

  useEffect(() => {
    if (!result && location.state?.result) {
      setResult(location.state.result)
    }
  }, [location.state, result])

  useEffect(() => {
    if (result) setContextResult(result)
  }, [result, setContextResult])

  const stories = (result?.stories ?? []).filter((s): s is NonNullable<typeof s> => s != null)

  const complexityToPoints: Record<string, number> = {
    XS: 1,
    S: 2,
    M: 3,
    L: 5,
    XL: 8,
  }
  const complexityToPriority: Record<string, "High" | "Medium" | "Low"> = {
    XS: "Low",
    S: "Low",
    M: "Medium",
    L: "High",
    XL: "High",
  }
  function getPoints(c: string): number {
    return complexityToPoints[c?.toUpperCase()] ?? 3
  }
  function getPriority(c: string): "High" | "Medium" | "Low" {
    return complexityToPriority[c?.toUpperCase()] ?? "Medium"
  }

  const exportJiraCsv = () => {
    if (stories.length === 0) return ""
    const header = "Summary,Description,Acceptance Criteria"
    const rows = stories.map(
      (s) =>
        `"${(s.title || "").replace(/"/g, '""')}","${(s.user_story || "").replace(/"/g, '""')}","${(s.acceptance_criteria || []).join("; ").replace(/"/g, '""')}"`
    )
    return [header, ...rows].join("\n")
  }

  const downloadCsv = () => {
    const csv = exportJiraCsv()
    const blob = new Blob([csv], { type: "text/csv" })
    const a = document.createElement("a")
    a.href = URL.createObjectURL(blob)
    a.download = "jira_import.csv"
    a.click()
    URL.revokeObjectURL(a.href)
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="flex items-center justify-between border-b bg-gradient-to-b from-[hsl(340_100%_27%_/0.02)] to-transparent px-8 pt-8 pb-6">
        <div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-foreground">
            {t("stories.title")}
          </h1>
          <p className="mt-1 text-muted-foreground">
            {t("stories.subtitle")}
          </p>
        {stories.length > 0 && (
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 rounded-lg bg-[hsl(340_100%_27%_/0.06)] px-4 py-2">
              <FileText className="h-5 w-5 text-primary" />
              <span className="font-serif text-2xl font-bold text-primary">
                <AnimatedNumber value={stories.length} />
              </span>
              <span className="text-sm text-muted-foreground">
                {t("stories.storiesGenerated")}
              </span>
            </div>
            <span className="text-sm text-muted-foreground">•</span>
            <span className="text-sm text-muted-foreground">
              {t("stories.readyForRefinement")}
            </span>
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
          <Button
            variant="outline"
            onClick={() => navigate("/feedback")}
            className="border-primary/30 text-primary hover:bg-primary/5"
          >
            {t("roadmap.newAnalysis")}
          </Button>
          {stories.length > 0 && (
            <Button variant="outline" onClick={downloadCsv}>
              <Download className="mr-2 h-4 w-4" />
              {t("stories.exportJira")}
            </Button>
          )}
        </div>
      </div>

      <div className="p-8">
      {!result ? (
        <Card className="thiga-card border-0">
          <CardContent className="py-12 text-center text-muted-foreground">
            <FileText className="mx-auto mb-4 h-12 w-12 opacity-50" />
            <p>{t("stories.runAnalysisHint")}</p>
            <Button className="btn-thiga mt-4" onClick={() => navigate("/feedback")}>
              {t("stories.analyzeFeedbacks")}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Tabs defaultValue="stories" className="space-y-6">
          <TabsList>
            <TabsTrigger value="stories">{t("stories.tabStories")}</TabsTrigger>
            {result?.stories_before_critique && result.stories_before_critique.length > 0 && (
              <TabsTrigger value="diff">
                <GitCompare className="mr-1.5 h-4 w-4" />
                {t("stories.diffCritique")}
              </TabsTrigger>
            )}
          </TabsList>
          <TabsContent value="stories" className="space-y-6">
          {stories.length === 0 ? (
            <Card className="thiga-card border-0">
              <CardContent className="py-12 text-center text-muted-foreground">
                <FileText className="mx-auto mb-4 h-12 w-12 opacity-50" />
                <p>{t("stories.emptyStories")}</p>
              </CardContent>
            </Card>
          ) : stories.map((s, i) => {
            const points = getPoints(s.complexity)
            const priority = getPriority(s.complexity)
            return (
              <Card key={i} className="thiga-card border-0">
                <CardHeader>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <CardTitle className="text-lg">US-{String(i + 1).padStart(3, "0")} {s.title}</CardTitle>
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          priority === "High"
                            ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
                            : priority === "Medium"
                            ? "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400"
                            : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                        }`}
                      >
                        {priority}
                      </span>
                      <span className="rounded-full bg-[hsl(340_100%_27%_/0.12)] px-2.5 py-0.5 text-xs font-bold text-primary">
                        {points}pts
                      </span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      {t("stories.userStory")}
                    </p>
                    <p>{s.user_story}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      {t("stories.acceptanceCriteria")}
                    </p>
                    <ul className="list-disc list-inside space-y-1">
                      {(s.acceptance_criteria || []).map((ac, j) => (
                        <li key={j}>{ac}</li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            )
          })}
          </TabsContent>
          {result?.stories_before_critique && result.stories_before_critique.length > 0 && (
            <TabsContent value="diff" className="space-y-6">
              <p className="text-sm text-muted-foreground">
                {t("stories.critiqueEffect")}
              </p>
              {(result.stories_before_critique || []).map((sBefore, i) => {
                const sAfter = (result?.stories ?? [])[i]
                if (!sBefore || !sAfter) return null
                const changed = JSON.stringify(sBefore) !== JSON.stringify(sAfter)
                if (!changed) {
                  return (
                    <Card key={i} className="thiga-card border-0 opacity-75">
                      <CardContent className="py-4">
                        <p className="text-sm text-muted-foreground">{t("stories.noChange", { n: i + 1 })}</p>
                      </CardContent>
                    </Card>
                  )
                }
                return (
                  <Card key={i} className="thiga-card border-0">
                    <CardHeader>
                      <CardTitle className="text-base">Story {i + 1} : {sAfter.title}</CardTitle>
                    </CardHeader>
                    <CardContent className="grid gap-4 md:grid-cols-2">
                      <div className="rounded-lg border border-amber-200 bg-amber-50/50 dark:bg-amber-900/10 p-4">
                        <p className="text-xs font-medium uppercase text-amber-700 dark:text-amber-400">{t("stories.before")}</p>
                        <p className="mt-2 text-sm">{sBefore.user_story}</p>
                        <ul className="mt-2 list-disc list-inside text-sm text-muted-foreground">
                          {(sBefore.acceptance_criteria || []).slice(0, 3).map((ac, j) => (
                            <li key={j}>{ac}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="rounded-lg border border-green-200 bg-green-50/50 dark:bg-green-900/10 p-4">
                        <p className="text-xs font-medium uppercase text-green-700 dark:text-green-400">{t("stories.afterRefinement")}</p>
                        <p className="mt-2 text-sm">{sAfter.user_story}</p>
                        <ul className="mt-2 list-disc list-inside text-sm text-muted-foreground">
                          {(sAfter.acceptance_criteria || []).slice(0, 3).map((ac, j) => (
                            <li key={j}>{ac}</li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </TabsContent>
          )}
        </Tabs>
      )}
      </div>
    </div>
  )
}
