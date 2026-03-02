import { useTranslation } from "react-i18next"
import { type Lang } from "@/lib/i18n"

export default function LanguageToggle() {
  const { i18n, t } = useTranslation()
  const current = (i18n.language?.slice(0, 2) ?? "fr") as Lang
  const next: Lang = current === "fr" ? "en" : "fr"

  const handleClick = () => {
    i18n.changeLanguage(next)
  }

  return (
    <button
      onClick={handleClick}
      className="flex h-9 min-w-[3rem] items-center justify-center rounded-lg border text-sm font-medium transition-all hover:bg-secondary"
      style={{
        borderColor: "hsl(var(--sidebar-border))",
        color: "hsl(var(--primary))",
      }}
      aria-label={t(`common.switchTo${next === "fr" ? "French" : "English"}`)}
      title={t(`common.switchTo${next === "fr" ? "French" : "English"}`)}
    >
      {next.toUpperCase()}
    </button>
  )
}
