import i18n from "i18next"
import { initReactI18next } from "react-i18next"
import fr from "@/locales/fr.json"
import en from "@/locales/en.json"

const STORAGE_KEY = "po-agent-lang"

export const supportedLangs = ["fr", "en"] as const
export type Lang = (typeof supportedLangs)[number]

function getInitialLang(): Lang {
  if (typeof window === "undefined") return "fr"
  const saved = localStorage.getItem(STORAGE_KEY) as Lang | null
  if (saved && supportedLangs.includes(saved)) return saved
  return navigator.language.startsWith("en") ? "en" : "fr"
}

i18n.use(initReactI18next).init({
  resources: { fr: { translation: fr }, en: { translation: en } },
  lng: getInitialLang(),
  fallbackLng: "fr",
  interpolation: { escapeValue: false },
})

i18n.on("languageChanged", (lng) => {
  if (typeof document !== "undefined") {
    document.documentElement.lang = lng.slice(0, 2)
  }
  if (typeof window !== "undefined") localStorage.setItem(STORAGE_KEY, lng)
})

if (typeof document !== "undefined") {
  document.documentElement.lang = i18n.language?.slice(0, 2) ?? "fr"
}

export default i18n
