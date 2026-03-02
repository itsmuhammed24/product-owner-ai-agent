import { useState, useEffect } from "react"
import { Sun, Moon } from "lucide-react"
import { getTheme, setTheme, type Theme } from "@/lib/theme"
import { useTranslation } from "react-i18next"

export default function ThemeToggle() {
  const { t } = useTranslation()
  const [theme, setThemeState] = useState<Theme>("light")

  useEffect(() => {
    setThemeState(getTheme())
  }, [])

  const handleToggle = () => {
    const next = theme === "dark" ? "light" : "dark"
    setTheme(next)
    setThemeState(next)
  }

  return (
    <button
      onClick={handleToggle}
      className="flex h-9 w-9 items-center justify-center rounded-lg border transition-all hover:bg-secondary"
      style={{
        borderColor: "hsl(var(--sidebar-border))",
        color: "hsl(var(--primary))",
      }}
      aria-label={theme === "dark" ? t("theme.light") : t("theme.dark")}
      title={theme === "dark" ? t("theme.switchToLight") : t("theme.switchToDark")}
    >
      {theme === "dark" ? (
        <Sun className="h-5 w-5" />
      ) : (
        <Moon className="h-5 w-5" />
      )}
    </button>
  )
}
