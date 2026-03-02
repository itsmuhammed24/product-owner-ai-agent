import { createContext, useContext, useState, type ReactNode } from "react"
import type { PipelineResult } from "@/lib/api"

type PipelineResultContextValue = {
  result: PipelineResult | null
  setResult: (r: PipelineResult | null) => void
}

const ctx = createContext<PipelineResultContextValue | null>(null)

export function PipelineResultProvider({ children }: { children: ReactNode }) {
  const [result, setResult] = useState<PipelineResult | null>(null)
  return (
    <ctx.Provider value={{ result, setResult }}>{children}</ctx.Provider>
  )
}

export function usePipelineResult() {
  const v = useContext(ctx)
  if (!v) throw new Error("usePipelineResult must be used within PipelineResultProvider")
  return v
}
