import type { FeedbackItem } from "@/lib/api"

const SAMPLE_URL = "/feedback_sample.jsonl"
const MINIMAL_URL = "/feedback_minimal.jsonl"
const DEFAULT_LIMIT = 8

async function loadFromUrl(url: string, limit?: number): Promise<FeedbackItem[]> {
  const res = await fetch(url)
  if (!res.ok) throw new Error("Sample introuvable")
  const text = await res.text()
  const parsed = text
    .trim()
    .split("\n")
    .filter(Boolean)
    .map((line) => JSON.parse(line) as FeedbackItem)
  return limit === undefined ? parsed : parsed.slice(0, limit)
}

export async function loadSampleFeedbacks(limit = DEFAULT_LIMIT): Promise<FeedbackItem[]> {
  return loadFromUrl(SAMPLE_URL, limit)
}

/** Exemple minimal 6 items — démo rapide */
export async function loadMinimalFeedbacks(): Promise<FeedbackItem[]> {
  return loadFromUrl(MINIMAL_URL)
}
