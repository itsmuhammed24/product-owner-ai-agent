export interface Stats {
  totalFeedbacks: number
  totalFeatures: number
  totalStories: number
  runCount: number
}

// Stats en mémoire uniquement : 0 au lancement, cumul à chaque run
const sessionStats: Stats = {
  totalFeedbacks: 0,
  totalFeatures: 0,
  totalStories: 0,
  runCount: 0,
}

export function getStats(): Stats {
  return { ...sessionStats }
}

export function addRunStats(feedbacks: number, features: number, stories: number) {
  sessionStats.totalFeedbacks += feedbacks
  sessionStats.totalFeatures += features
  sessionStats.totalStories += stories
  sessionStats.runCount += 1
}

export function resetStats() {
  sessionStats.totalFeedbacks = 0
  sessionStats.totalFeatures = 0
  sessionStats.totalStories = 0
  sessionStats.runCount = 0
}

export function estimateHoursSaved(stats: Stats): number {
  // ~3 min/feedback + ~9 min/story en temps PO manuel évité
  return Math.round((stats.totalFeedbacks * 3 + stats.totalStories * 9) / 60)
}
