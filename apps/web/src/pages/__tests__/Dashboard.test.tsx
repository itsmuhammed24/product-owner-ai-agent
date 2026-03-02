import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { BrowserRouter } from "react-router-dom"
import Dashboard from "../Dashboard"
import * as stats from "@/lib/stats"

vi.mock("@/contexts/PipelineResultContext", () => ({
  usePipelineResult: () => ({ result: null, setResult: vi.fn() }),
}))

function Wrapper({ children }: { children: React.ReactNode }) {
  return <BrowserRouter>{children}</BrowserRouter>
}

describe("Dashboard", () => {
  beforeEach(() => {
    vi.spyOn(stats, "resetStats").mockImplementation(() => {})
    vi.spyOn(stats, "getStats").mockReturnValue({
      totalFeedbacks: 5,
      totalFeatures: 3,
      totalStories: 8,
      runCount: 2,
    })
  })

  it("renders session metrics and reset button", () => {
    vi.stubGlobal("confirm", vi.fn(() => true))
    render(
      <Wrapper>
        <Dashboard />
      </Wrapper>
    )
    expect(screen.getByText(/Session metrics|Métriques de session/i)).toBeInTheDocument()
    const resetBtn = screen.getByRole("button", { name: /réinitialiser|reset/i })
    expect(resetBtn).toBeInTheDocument()
    fireEvent.click(resetBtn)
    expect(stats.resetStats).toHaveBeenCalled()
    vi.unstubAllGlobals()
  })
})
