import { apiGet } from './client'
import type { PredictionResult } from './types'

export function getPrediction(id: number): Promise<PredictionResult> {
  return apiGet<PredictionResult>(`/prediction/${id}`)
}
