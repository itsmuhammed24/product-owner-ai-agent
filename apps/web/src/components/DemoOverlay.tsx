import { useState, useEffect } from "react"
import {
  MessageSquare,
  Lightbulb,
  ListOrdered,
  FileText,
  Check,
  ArrowRight,
  Loader2,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { runPipeline, type PipelineResult } from "@/lib/api"
import { addRunStats } from "@/lib/stats"
import { loadSampleFeedbacks } from "@/lib/sampleFeedback"
import { usePipelineResult } from "@/contexts/PipelineResultContext"
import { AnimatedNumber } from "./AnimatedNumber"
import { useTranslation } from "react-i18next"

const STEPS = [
  { id: "feedback", icon: MessageSquare },
  { id: "insights", icon: Lightbulb },
  { id: "backlog", icon: ListOrdered },
  { id: "stories", icon: FileText },
] as const

type StepId = (typeof STEPS)[number]["id"]
const STEP_ORDER: StepId[] = ["feedback", "insights", "backlog", "stories"]

export default function DemoOverlay({
  open,
  onClose,
  onComplete,
}: {
  open: boolean
  onClose: () => void
  onComplete: (result: PipelineResult) => void
}) {
  const [phase, setPhase] = useState<"intro" | "running" | "done">("intro")
  const [currentStep, setCurrentStep] = useState<StepId | null>(null)
  const [result, setResult] = useState<PipelineResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const { setResult: setContextResult } = usePipelineResult()
  const { t } = useTranslation()

  useEffect(() => {
    if (!open) return
    setPhase("intro")
    setCurrentStep(null)
    setResult(null)
    setError(null)
  }, [open])

  const runDemo = async () => {
    setPhase("running")
    setError(null)

    let stepIdx = 0

    const advanceStep = () => {
      if (stepIdx < STEP_ORDER.length) {
        setCurrentStep(STEP_ORDER[stepIdx])
        stepIdx++
      }
    }

    advanceStep()
    const stepInterval = setInterval(advanceStep, 2000)

    try {
      const items = await loadSampleFeedbacks(8)
      clearInterval(stepInterval)
      setCurrentStep("stories")

      const data = await runPipeline(items)
      addRunStats(
        items.length,
        data.backlog?.length ?? 0,
        (data.stories ?? []).filter(Boolean).length
      )
      setResult(data)
      setContextResult(data)
      setPhase("done")
    } catch (err) {
      clearInterval(stepInterval)
      setError(err instanceof Error ? err.message : t("common.error"))
      setPhase("done")
    }
  }

  const handleExplore = () => {
    if (result) onComplete(result)
    onClose()
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-background/95 backdrop-blur-md">
      <div className="flex w-full max-w-lg flex-col items-center px-8 py-12">
        {phase === "intro" && (
          <>
            <div className="mb-8 flex items-center gap-3">
              <img
                src="/thiga-logo.png"
                alt="Thiga"
                className="h-12 w-12 rounded-xl object-contain"
              />
              <div className="text-left">
                <h2 className="font-serif text-2xl font-bold">{t("demo.title")}</h2>
                <p className="text-sm text-muted-foreground">
                  {t("demo.subtitle")}
                </p>
              </div>
            </div>
            <p className="mb-8 text-center text-muted-foreground">
              {t("demo.intro")}
            </p>
            <div className="mb-6 flex gap-3">
              {STEPS.map((s) => (
                <div
                  key={s.id}
                  className="flex flex-col items-center gap-1 rounded-lg border px-4 py-2"
                  style={{ borderColor: "hsl(var(--border))" }}
                >
                  <s.icon className="h-5 w-5 text-primary" />
                  <span className="text-xs text-muted-foreground">{t(`demo.steps.${s.id}`).split(" ")[0]}</span>
                </div>
              ))}
            </div>
            <Button size="lg" className="btn-thiga" onClick={runDemo}>
              {t("demo.launch")}
            </Button>
          </>
        )}

        {phase === "running" && (
          <>
            <Loader2 className="mb-6 h-12 w-12 animate-spin text-primary" />
            <h2 className="mb-2 font-serif text-xl font-semibold">{t("demo.running")}</h2>
            <div className="mb-8 flex flex-col gap-3">
              {STEPS.map((s) => (
                <div
                  key={s.id}
                  className={`flex items-center gap-3 rounded-lg border px-4 py-3 transition-colors ${
                    currentStep === s.id
                      ? "border-primary bg-primary/5"
                      : "border-transparent bg-muted/30"
                  }`}
                >
                  {currentStep === s.id ? (
                    <Loader2 className="h-5 w-5 shrink-0 animate-spin text-primary" />
                  ) : (
                    <s.icon className="h-5 w-5 shrink-0 text-muted-foreground" />
                  )}
                  <span
                    className={
                      currentStep === s.id ? "font-medium" : "text-muted-foreground"
                    }
                  >
                    {t(`demo.steps.${s.id}`)}
                  </span>
                  {STEP_ORDER.indexOf(s.id) < STEP_ORDER.indexOf(currentStep ?? "feedback") && (
                    <Check className="ml-auto h-5 w-5 text-green-600" />
                  )}
                </div>
              ))}
            </div>
          </>
        )}

        {(phase === "done" && result) && (
          <>
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
              <Check className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
            <h2 className="mb-2 font-serif text-2xl font-bold">{t("demo.done")}</h2>
            <p className="mb-8 text-center text-muted-foreground">
              {t("demo.doneDesc")}
            </p>
            <div className="mb-8 flex gap-6">
              <div className="flex flex-col items-center rounded-xl border px-6 py-4" style={{ borderColor: "hsl(var(--border))" }}>
                <AnimatedNumber value={result.insights?.length ?? 0} className="font-serif text-3xl font-bold text-primary" />
                <span className="text-xs text-muted-foreground">{t("demo.insights")}</span>
              </div>
              <div className="flex flex-col items-center rounded-xl border px-6 py-4" style={{ borderColor: "hsl(var(--border))" }}>
                <AnimatedNumber value={result.backlog?.length ?? 0} className="font-serif text-3xl font-bold text-primary" />
                <span className="text-xs text-muted-foreground">{t("demo.backlog")}</span>
              </div>
              <div className="flex flex-col items-center rounded-xl border px-6 py-4" style={{ borderColor: "hsl(var(--border))" }}>
                <AnimatedNumber value={(result.stories ?? []).filter(Boolean).length} className="font-serif text-3xl font-bold text-primary" />
                <span className="text-xs text-muted-foreground">{t("demo.stories")}</span>
              </div>
            </div>
            <Button size="lg" className="btn-thiga" onClick={handleExplore}>
              {t("demo.explore")}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </>
        )}

        {(phase === "done" && error) && (
          <>
            <p className="mb-6 text-center text-red-600 dark:text-red-400">{error}</p>
            <Button variant="outline" onClick={onClose}>
              {t("demo.close")}
            </Button>
          </>
        )}

        <button
          onClick={onClose}
          className="mt-8 text-sm text-muted-foreground underline hover:text-foreground"
        >
          {t("demo.close")}
        </button>
      </div>
    </div>
  )
}
