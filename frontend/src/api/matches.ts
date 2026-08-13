import { apiGet } from './client'
import type { Match } from './types'

export function getMatches(): Promise<Match[]> {
  return apiGet<Match[]>('/matches/')
}

export function getMatch(id: number): Promise<Match> {
  return apiGet<Match>(`/matches/${id}`)
}
