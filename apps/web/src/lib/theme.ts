const STORAGE_KEY = "po_agent_theme"

export type Theme = "light" | "dark"

export function getTheme(): Theme {
  if (typeof window === "undefined") return "light"
  const stored = localStorage.getItem(STORAGE_KEY) as Theme | null
  if (stored === "dark" || stored === "light") return stored
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
}

export function setTheme(theme: Theme) {
  localStorage.setItem(STORAGE_KEY, theme)
  document.documentElement.classList.toggle("dark", theme === "dark")
}

export function toggleTheme(): Theme {
  const next = getTheme() === "dark" ? "light" : "dark"
  setTheme(next)
  return next
}

export function initTheme() {
  setTheme(getTheme())
}
