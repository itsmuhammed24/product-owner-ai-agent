import { createContext, useContext, useState, type ReactNode } from "react"

const ctx = createContext<{ isPresentation: boolean; setPresentation: (v: boolean) => void } | null>(null)

export function PresentationProvider({ children }: { children: ReactNode }) {
  const [isPresentation, setPresentation] = useState(false)
  return (
    <ctx.Provider value={{ isPresentation, setPresentation }}>{children}</ctx.Provider>
  )
}

export function usePresentation() {
  const v = useContext(ctx)
  if (!v) return { isPresentation: false, setPresentation: () => {} }
  return v
}
