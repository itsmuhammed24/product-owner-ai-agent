import { Component, type ErrorInfo, type ReactNode } from "react"
import { Button } from "@/components/ui/button"
import { AlertTriangle } from "lucide-react"
import i18n from "@/lib/i18n"

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo)
  }

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) return this.props.fallback
      return (
        <div
          className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-8 text-center"
          role="alert"
        >
          <AlertTriangle className="h-16 w-16 text-amber-500" aria-hidden />
          <h2 className="font-serif text-xl font-bold text-foreground">
            {i18n.t("common.errorOccurred")}
          </h2>
          <p className="max-w-md text-sm text-muted-foreground">
            {this.state.error.message}
          </p>
          <Button
            onClick={() => this.setState({ hasError: false, error: undefined })}
            variant="outline"
          >
            {i18n.t("common.retry")}
          </Button>
        </div>
      )
    }
    return this.props.children
  }
}
