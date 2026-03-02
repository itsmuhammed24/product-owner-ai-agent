import { useMemo } from "react"

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^\wàâäéèêëïîôùûüç\s-]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 2 && !/^\d+$/.test(w))
}

const STOP_WORDS = new Set([
  "les", "des", "une", "pour", "dans", "avec", "sur", "que", "qui", "est", "sont",
  "pas", "plus", "tout", "très", "aussi", "bien", "fait", "font", "avoir", "être",
  "the", "and", "for", "with", "that", "this", "from", "your", "can", "have",
])

export default function WordCloud({
  insights,
  maxWords = 24,
  className = "",
}: {
  insights: Array<{ request?: string; theme?: string }>
  maxWords?: number
  className?: string
}) {
  const words = useMemo(() => {
    const counts = new Map<string, number>()
    for (const i of insights) {
      const text = `${i.request ?? ""} ${i.theme ?? ""}`
      for (const w of tokenize(text)) {
        if (!STOP_WORDS.has(w)) {
          counts.set(w, (counts.get(w) ?? 0) + 1)
        }
      }
    }
    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, maxWords)
      .map(([word, count]) => ({ word, count }))
  }, [insights, maxWords])

  if (words.length === 0) return null

  const maxCount = Math.max(...words.map((w) => w.count))
  const minSize = 0.75
  const maxSize = 1.5

  return (
    <div className={`flex flex-wrap items-center justify-center gap-2 p-4 ${className}`}>
      {words.map(({ word, count }) => {
        const ratio = maxCount > 0 ? count / maxCount : 0
        const size = minSize + ratio * (maxSize - minSize)
        return (
          <span
            key={word}
            className="rounded-full px-2 py-1 text-primary transition-colors hover:bg-primary/10"
            style={{
              fontSize: `${size}rem`,
              fontWeight: 500 + Math.round(ratio * 200),
              opacity: 0.7 + ratio * 0.3,
            }}
          >
            {word}
          </span>
        )
      })}
    </div>
  )
}
