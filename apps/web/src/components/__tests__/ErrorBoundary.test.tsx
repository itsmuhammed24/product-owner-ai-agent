import { describe, it, expect, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import ErrorBoundary from "../ErrorBoundary"

const ThrowError = () => {
  throw new Error("Test error")
}

describe("ErrorBoundary", () => {
  it("renders children when no error", () => {
    render(
      <ErrorBoundary>
        <div>Content</div>
      </ErrorBoundary>
    )
    expect(screen.getByText("Content")).toBeInTheDocument()
  })

  it("renders fallback when child throws", () => {
    vi.spyOn(console, "error").mockImplementation(() => {})
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )
    expect(screen.getByRole("alert")).toBeInTheDocument()
    expect(screen.getByText("Test error")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /retry|réessayer/i })).toBeInTheDocument()
    vi.restoreAllMocks()
  })
})
