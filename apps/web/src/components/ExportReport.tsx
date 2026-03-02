import { Button } from "@/components/ui/button"
import { Download, Share2 } from "lucide-react"
import type { PipelineResult } from "@/lib/api"
import { formatRiceScore } from "@/lib/utils"

function getReportHtml(result: PipelineResult): string {
  const topBacklog = (result.backlog ?? []).slice(0, 5)
  const topStories = (result.stories ?? []).filter((s): s is NonNullable<typeof s> => s != null).slice(0, 3)
  const insights = result.insights ?? []

  return `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>PO Agent — Rapport d'analyse</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 2rem; max-width: 800px; margin: 0 auto; color: #333; }
    h1 { font-size: 1.75rem; margin-bottom: 0.5rem; color: #7c2d3a; }
    h2 { font-size: 1.1rem; margin: 1.5rem 0 0.75rem; color: #7c2d3a; border-bottom: 2px solid #7c2d3a; padding-bottom: 0.25rem; }
    .meta { font-size: 0.875rem; color: #666; margin-bottom: 2rem; }
    .card { background: #f8f8f8; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
    .score { font-weight: 700; color: #7c2d3a; }
    footer { margin-top: 2rem; font-size: 0.75rem; color: #999; text-align: center; }
  </style>
</head>
<body>
  <h1>PO Agent — Rapport d'analyse</h1>
  <p class="meta">Généré par PO Agent by Thiga • ${new Date().toLocaleDateString("fr-FR")}</p>
  <h2>Résumé</h2>
  <p>${insights.length} insights • ${result.backlog?.length ?? 0} items backlog • ${(result.stories ?? []).filter(Boolean).length} user stories</p>
  <h2>Top priorités (RICE)</h2>
  ${topBacklog.map((b) => `<div class="card"><span class="score">${formatRiceScore(b.rice_score)}</span> — ${b.feature}<br><small>${b.rationale?.slice(0, 100)}…</small></div>`).join("")}
  <h2>User stories clés</h2>
  ${topStories.map((s) => `<div class="card"><strong>${s.title}</strong> — ${s.complexity}</div>`).join("")}
  <footer>PO Agent by Thiga — thiga.co</footer>
</body>
</html>`
}

export function exportPitchDeck(result: PipelineResult) {
  const html = getReportHtml(result)
  const blob = new Blob([html], { type: "text/html" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `po-agent-rapport-${new Date().toISOString().slice(0, 10)}.html`
  a.click()
  URL.revokeObjectURL(url)
}

export default function ExportReport({
  result,
  onExport,
}: {
  result: PipelineResult | null
  onExport?: () => void
}) {
  if (!result) return null

  const handleShare = async () => {
    const html = getReportHtml(result)
    const blob = new Blob([html], { type: "text/html" })
    const file = new File([blob], `po-agent-rapport-${new Date().toISOString().slice(0, 10)}.html`, { type: "text/html" })
    if (navigator.share && navigator.canShare?.({ files: [file] })) {
      try {
        await navigator.share({
          title: "Rapport PO Agent",
          text: "Rapport d'analyse feedback — PO Agent by Thiga",
          files: [file],
        })
        onExport?.()
      } catch {
        exportPitchDeck(result)
        onExport?.()
      }
    } else {
      exportPitchDeck(result)
      onExport?.()
    }
  }

  return (
    <div className="flex gap-2">
      <Button
        variant="outline"
        size="sm"
        onClick={() => {
          exportPitchDeck(result)
          onExport?.()
        }}
        className="border-primary/30 text-primary hover:bg-primary/5"
      >
        <Download className="mr-2 h-4 w-4" />
        Exporter
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={() => {
          handleShare()
          onExport?.()
        }}
        className="border-primary/30 text-primary hover:bg-primary/5"
      >
        <Share2 className="mr-2 h-4 w-4" />
        Partager
      </Button>
    </div>
  )
}
