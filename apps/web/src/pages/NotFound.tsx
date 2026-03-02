import { Link } from "react-router-dom"
import { FileQuestion } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useTranslation } from "react-i18next"

export default function NotFound() {
  const { t } = useTranslation()
  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center gap-6 p-8 text-center">
      <FileQuestion className="h-24 w-24 text-muted-foreground/50" aria-hidden />
      <div>
        <h1 className="font-serif text-4xl font-bold text-foreground">404</h1>
        <p className="mt-2 text-muted-foreground">{t("common.notFound")}</p>
      </div>
      <Button asChild variant="outline" size="lg">
        <Link to="/">{t("common.backHome")}</Link>
      </Button>
    </div>
  )
}
