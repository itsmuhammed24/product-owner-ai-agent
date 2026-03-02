import { useState, useEffect } from "react"
import { NavLink } from "react-router-dom"
import { useTranslation } from "react-i18next"
import {
  LayoutDashboard,
  MessageSquareText,
  Map,
  FileText,
} from "lucide-react"
import ThemeToggle from "./ThemeToggle"
import LanguageToggle from "./LanguageToggle"
import { checkHealth } from "@/lib/api"

const navKeys = [
  { to: "/", icon: LayoutDashboard, key: "dashboard" },
  { to: "/feedback", icon: MessageSquareText, key: "feedback" },
  { to: "/roadmap", icon: Map, key: "roadmap" },
  { to: "/stories", icon: FileText, key: "stories" },
] as const

export default function AppSidebar() {
  const { t } = useTranslation()
  const [online, setOnline] = useState<boolean | null>(null)

  useEffect(() => {
    const update = (h: Awaited<ReturnType<typeof checkHealth>>) => {
      setOnline(h.ok)
    }
    checkHealth().then(update)
    const t = setInterval(() => checkHealth().then(update), 30000)
    return () => clearInterval(t)
  }, [])

  return (
    <aside
      className="flex h-screen w-64 flex-col border-r"
      style={{
        background: "hsl(var(--sidebar-bg))",
        borderColor: "hsl(var(--sidebar-border))",
      }}
      role="complementary"
      aria-label={t("sidebar.appName")}
    >
      <div className="flex h-20 items-center justify-between border-b px-6" style={{ borderColor: "hsl(var(--sidebar-border))" }}>
        <div className="flex items-center gap-3">
          <img
            src="/thiga-logo.png"
            alt="Thiga"
            className="h-10 w-10 shrink-0 rounded-xl object-contain"
          />
          <div>
          <span
            className="block font-serif text-lg font-bold leading-tight"
            style={{ color: "hsl(var(--sidebar-fg))" }}
          >
            {t("sidebar.appName")}
          </span>
          <span
            className="block text-xs opacity-60"
            style={{ color: "hsl(var(--sidebar-fg))" }}
          >
            {t("sidebar.byCreator")}
          </span>
          {online !== null && (
            <span className="mt-0.5 flex flex-col gap-0.5 text-xs">
              <span className="flex items-center gap-1">
                <span
                  className={`inline-block h-1.5 w-1.5 rounded-full ${
                    online ? "bg-green-500" : "bg-amber-500"
                  }`}
                />
                {online ? t("common.online") : t("common.offline")}
              </span>
            </span>
          )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <LanguageToggle />
          <ThemeToggle />
        </div>
      </div>
      <nav className="flex-1 space-y-0.5 p-4" role="navigation" aria-label={t("sidebar.navLabel")}>
        {navKeys.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                isActive
                  ? "bg-[hsl(340_100%_27%_/_0.08)] text-[hsl(340_100%_27%)]"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`
            }
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {t(`sidebar.${item.key}`)}
          </NavLink>
        ))}
      </nav>
      <div
        className="border-t p-4"
        style={{ borderColor: "hsl(var(--sidebar-border))" }}
      >
        <p
          className="text-xs leading-relaxed text-muted-foreground"
        >
          {t("sidebar.tagline")}
        </p>
      </div>
    </aside>
  )
}
