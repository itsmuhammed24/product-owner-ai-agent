import { describe, it, expect, vi } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { BrowserRouter } from "react-router-dom"
import AppSidebar from "../AppSidebar"

vi.mock("@/lib/api", () => ({
  checkHealth: vi.fn().mockResolvedValue({ ok: true }),
}))

function Wrapper({ children }: { children: React.ReactNode }) {
  return <BrowserRouter>{children}</BrowserRouter>
}

describe("AppSidebar", () => {
  it("renders navigation links", async () => {
    render(
      <Wrapper>
        <AppSidebar />
      </Wrapper>
    )
    await waitFor(() => {
      expect(screen.getByText(/Online|En ligne/i)).toBeInTheDocument()
    })
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument()
    expect(screen.getByText(/Feedback Analysis|Analyse Feedback/i)).toBeInTheDocument()
    expect(screen.getByText(/Roadmap/i)).toBeInTheDocument()
    expect(screen.getByText(/User Stories/i)).toBeInTheDocument()
  })
})
