import { apiGet } from './client'
import type { Competition } from './types'

export function getCompetitions(): Promise<Competition[]> {
  return apiGet<Competition[]>('/competitions/')
}
