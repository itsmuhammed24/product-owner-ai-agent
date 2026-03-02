import { useState, useEffect } from "react"
import { Link, useNavigate } from "react-router-dom"
import {
  MessageSquare,
  Target,
  FileText,
  Clock,
  BarChart3,
  Clapperboard,
  Zap,
  ChevronRight,
  GitBranch,
  RefreshCw,
  RotateCcw,
  TrendingUp,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AnimatedNumber } from "@/components/AnimatedNumber"
import { getStats, estimateHoursSaved, resetStats } from "@/lib/stats"
import { usePipelineResult } from "@/contexts/PipelineResultContext"
import DemoOverlay from "@/components/DemoOverlay"
import ThigaValues from "@/components/ThigaValues"
import { useTranslation } from "react-i18next"

function MetricCard({
  title,
  value,
  suffix = "",
  trend,
  icon: Icon,
  to,
}: {
  title: string
  value: number
  suffix?: string
  trend?: string
  icon: React.ElementType
  to?: string
}) {
  const card = (
    <Card className={`thiga-card group overflow-hidden border-0 ${to ? "cursor-pointer transition-all hover:border-primary/30 hover:shadow-md" : ""}`}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="mt-2 font-serif text-3xl font-bold leading-none tracking-tight text-foreground tabular-nums text-left">
              <AnimatedNumber value={value} suffix={suffix} />
            </p>
            {trend && (
              <p className="trend-bordeaux mt-1.5 flex items-center gap-1 text-sm font-medium">
                <TrendingUp className="h-4 w-4" />
                {trend}
              </p>
            )}
          </div>
          <div className="rounded-xl bg-[hsl(340_100%_27%_/0.08)] p-3 transition-colors group-hover:bg-[hsl(340_100%_27%_/0.12)]">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
  return to ? <Link to={to} aria-label={title}>{card}</Link> : card
}

const CAPABILITIES = [
  {
    id: "stories",
    icon: FileText,
    titleKey: "userStories",
    descKey: "userStoriesDesc",
    outputKey: "userStoriesOutput",
    to: "/stories",
    initialTab: null,
  },
  {
    id: "priorisation",
    icon: Target,
    titleKey: "priorisation",
    descKey: "priorisationDesc",
    outputKey: "priorisationOutput",
    to: "/roadmap",
    initialTab: "backlog",
  },
  {
    id: "sprint",
    icon: BarChart3,
    titleKey: "sprintPlanning",
    descKey: "sprintPlanningDesc",
    outputKey: "sprintPlanningOutput",
    to: "/roadmap",
    initialTab: "roadmap",
  },
  {
    id: "dependencies",
    icon: GitBranch,
    titleKey: "dependencies",
    descKey: "dependenciesDesc",
    outputKey: "dependenciesOutput",
    to: "/roadmap",
    initialTab: "insights",
  },
  {
    id: "impact",
    icon: TrendingUp,
    titleKey: "impactAnalysis",
    descKey: "impactAnalysisDesc",
    outputKey: "impactAnalysisOutput",
    to: "/feedback",
    initialTab: null,
  },
  {
    id: "refinement",
    icon: RefreshCw,
    titleKey: "autoRefinement",
    descKey: "autoRefinementDesc",
    outputKey: "autoRefinementOutput",
    to: "/stories",
    initialTab: null,
  },
] as const

function CapabilitiesSection({
  navigate,
}: {
  navigate: (to: string, opts?: { state?: Record<string, unknown> }) => void
}) {
  const { t } = useTranslation()
  const { result } = usePipelineResult()
  const handleTry = (cap: (typeof CAPABILITIES)[number]) => {
    navigate(cap.to, {
      state: {
        ...(result && { result }),
        ...(cap.initialTab && { initialTab: cap.initialTab }),
      },
    })
  }

  return (
    <section className="mt-16" aria-labelledby="capabilities-heading">
      <div className="mb-8">
        <h2 id="capabilities-heading" className="font-serif text-2xl font-semibold tracking-tight text-foreground">
          {t("dashboard.whatAgentCanDo")}
        </h2>
        <p className="mt-1 text-muted-foreground">
          {t("dashboard.sixCapabilities")}
        </p>
      </div>
      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
        {CAPABILITIES.map((cap) => {
          const Icon = cap.icon
          return (
            <Card
              key={cap.id}
              className="group thiga-card border-0 transition-all duration-200 hover:border-primary/25 hover:shadow-lg hover:shadow-primary/5"
              role="article"
              aria-labelledby={`cap-${cap.id}-title`}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[hsl(340_100%_27%_/0.1)] transition-colors group-hover:bg-[hsl(340_100%_27%_/0.15)]">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <CardTitle id={`cap-${cap.id}-title`} className="font-serif text-base font-semibold leading-tight">
                        {t(`dashboard.${cap.titleKey}`)}
                      </CardTitle>
                      <p className="mt-0.5 text-sm text-muted-foreground">
                        {t(`dashboard.${cap.descKey}`)}
                      </p>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-xs font-medium text-primary/80">
                  → {t(`dashboard.${cap.outputKey}`)}
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full border-primary/30 text-primary transition-colors hover:bg-primary/10 hover:border-primary/50 focus-visible:ring-2 focus-visible:ring-primary"
                  onClick={() => handleTry(cap)}
                  aria-label={`${t("dashboard.try")} — ${t(`dashboard.${cap.titleKey}`)}`}
                >
                  {t("dashboard.try")}
                  <ChevronRight className="ml-1.5 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </section>
  )
}

export default function Dashboard() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [stats, setStats] = useState(() => getStats())
  const [demoOverlayOpen, setDemoOverlayOpen] = useState(false)
  const hours = estimateHoursSaved(stats)

  useEffect(() => {
    const refresh = () => setStats(getStats())
    refresh()
    document.addEventListener("visibilitychange", refresh)
    return () => document.removeEventListener("visibilitychange", refresh)
  }, [])

  return (
    <main className="min-h-screen bg-background" role="main" aria-label={t("dashboard.title")}>
      <header className="flex flex-col gap-4 border-b bg-gradient-to-b from-[hsl(340_100%_27%_/0.02)] to-transparent px-8 pt-8 pb-6 sm:flex-row sm:items-end sm:justify-between" role="banner">
        <div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Zap className="h-4 w-4 text-primary" />
            <span>{t("dashboard.assistantSubtitle")}</span>
          </div>
          <h1 className="mt-2 font-serif text-3xl font-bold tracking-tight text-foreground">
            {t("dashboard.title")}
          </h1>
          <p className="mt-1 text-muted-foreground">
            {t("dashboard.pipelineFlow")}
          </p>
        </div>
        <Button onClick={() => setDemoOverlayOpen(true)} className="btn-thiga shrink-0" aria-label={t("dashboard.launchDemo")}>
          <Clapperboard className="mr-2 h-4 w-4" />
          {t("dashboard.launchDemo")}
        </Button>
      </header>

      <section className="p-8" aria-labelledby="session-metrics-heading">
        <div className="mb-4 flex items-center justify-between">
          <span id="session-metrics-heading" className="text-sm font-medium text-muted-foreground">{t("dashboard.sessionMetrics")}</span>
          <Button
            variant="ghost"
            size="sm"
            disabled={stats.runCount === 0}
            onClick={() => {
              if (window.confirm(t("dashboard.resetConfirm"))) {
                resetStats()
                setStats(getStats())
              }
            }}
            className="h-8 gap-1.5 text-muted-foreground hover:text-foreground disabled:opacity-50"
            aria-label={t("dashboard.resetStats")}
          >
            <RotateCcw className="h-4 w-4" />
            {t("dashboard.resetStats")}
          </Button>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title={t("dashboard.metricFeedbacks")}
            value={stats.totalFeedbacks}
            icon={MessageSquare}
            to="/feedback"
          />
          <MetricCard
            title={t("dashboard.metricFeatures")}
            value={stats.totalFeatures}
            icon={Target}
            to="/roadmap"
          />
          <MetricCard
            title={t("dashboard.metricStories")}
            value={stats.totalStories}
            icon={FileText}
            to="/stories"
          />
          <MetricCard
            title={t("dashboard.metricHours")}
            value={hours}
            suffix="h"
            icon={Clock}
          />
        </div>

        <CapabilitiesSection navigate={navigate} />

        <div className="mt-12">
          <ThigaValues />
        </div>

        <DemoOverlay
        open={demoOverlayOpen}
        onClose={() => setDemoOverlayOpen(false)}
        onComplete={(data) => {
          setStats(getStats())
          navigate("/roadmap", { state: { result: data } })
        }}
      />
      </section>
    </main>
  )
}
