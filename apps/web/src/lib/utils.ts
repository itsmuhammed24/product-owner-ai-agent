import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Affiche le score RICE : 2 décimales si < 1, 1 si < 10, entier sinon */
export function formatRiceScore(score: number): string {
  if (score >= 10) return Math.round(score).toString()
  if (score >= 1) return score.toFixed(1)
  return score.toFixed(2)
}
