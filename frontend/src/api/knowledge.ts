import { apiGet } from './client'
import type { MatchProfile } from './types'

export function getMatchKnowledge(id: number): Promise<MatchProfile> {
  return apiGet<MatchProfile>(`/knowledge/${id}`)
}
