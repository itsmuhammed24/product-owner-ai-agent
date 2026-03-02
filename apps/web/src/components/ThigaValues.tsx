import { Zap, Heart, Shield, Trophy } from "lucide-react"

const VALUES = [
  {
    icon: Zap,
    title: "Stay hungry, stay foolish",
    desc: "Curiosité et audace pour nourrir l'innovation.",
  },
  {
    icon: Heart,
    title: "Pay it forward",
    desc: "Générosité : on donne temps et savoir sans attendre de retour.",
  },
  {
    icon: Shield,
    title: "Do the right thing",
    desc: "Intégrité et transparence dans chaque décision.",
  },
  {
    icon: Trophy,
    title: "Be among the best",
    desc: "Excellence et standards élevés en tout.",
  },
] as const

export default function ThigaValues() {
  return (
    <div className="rounded-xl border p-4" style={{ borderColor: "hsl(var(--border))" }}>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap gap-6">
          {VALUES.map((v) => (
            <div key={v.title} className="flex items-center gap-2">
              <v.icon className="h-4 w-4 shrink-0 text-primary" />
              <span className="text-sm font-medium">{v.title}</span>
            </div>
          ))}
        </div>
        <a
          href="https://www.thiga.co/fr/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-medium text-primary hover:underline"
        >
          Découvrir Thiga →
        </a>
      </div>
    </div>
  )
}
