import { useState, useEffect, useRef } from "react"
import { useTranslation } from "react-i18next"

interface AnimatedNumberProps {
  value: number
  duration?: number
  suffix?: string
  className?: string
}

const langToLocale: Record<string, string> = {
  fr: "fr-FR",
  en: "en-US",
}

export function AnimatedNumber({
  value,
  duration = 800,
  suffix = "",
  className = "",
}: AnimatedNumberProps) {
  const { i18n } = useTranslation()
  const [display, setDisplay] = useState(0)
  const prevRef = useRef(0)
  const locale = langToLocale[i18n.language] ?? i18n.language ?? "fr-FR"

  useEffect(() => {
    const start = prevRef.current
    prevRef.current = value
    const diff = value - start
    const startTime = performance.now()

    const step = (now: number) => {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const easeOut = 1 - Math.pow(1 - progress, 3)
      setDisplay(Math.round(start + diff * easeOut))

      if (progress < 1) {
        requestAnimationFrame(step)
      }
    }

    requestAnimationFrame(step)
  }, [value, duration])

  return (
    <span className={`inline tabular-nums ${className}`.trim()}>
      {display.toLocaleString(locale)}
      {suffix && <span className="ml-1">{suffix}</span>}
    </span>
  )
}

