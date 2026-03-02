import { describe, it, expect } from "vitest"
import { formatRiceScore } from "../utils"

describe("formatRiceScore", () => {
  it("formats score >= 10 as integer", () => {
    expect(formatRiceScore(12.5)).toBe("13")
    expect(formatRiceScore(100)).toBe("100")
  })

  it("formats score 1-10 with 1 decimal", () => {
    expect(formatRiceScore(5.25)).toBe("5.3")
    expect(formatRiceScore(1)).toBe("1.0")
  })

  it("formats score < 1 with 2 decimals", () => {
    expect(formatRiceScore(0.25)).toBe("0.25")
    expect(formatRiceScore(0.5)).toBe("0.50")
  })
})
