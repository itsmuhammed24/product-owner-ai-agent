import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import "@/lib/i18n"
import "./index.css"
import { initTheme } from "@/lib/theme"
import { PipelineResultProvider } from "@/contexts/PipelineResultContext"
import { PresentationProvider } from "@/contexts/PresentationContext"
import ErrorBoundary from "@/components/ErrorBoundary"
import App from './App.tsx'

initTheme()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <PipelineResultProvider>
        <PresentationProvider>
          <App />
        </PresentationProvider>
      </PipelineResultProvider>
    </ErrorBoundary>
  </StrictMode>,
)
