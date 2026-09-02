/**
 * Types mirror the backend's OpenAPI schema exactly (pulled live from
 * the running backend, not guessed). Do not add fields the API
 * doesn't return, and do not compute derived intelligence here - the
 * backend is the intelligence engine.
 */

export type MatchStatus = string

export interface Match {
  id: number
  home_team: string
  away_team: string
  competition: string
  kickoff: string
  home_score: number | null
  away_score: number | null
  status: MatchStatus
}

export interface HeadToHead {
  matches?: number
  home_wins: number
  draws: number
  away_wins: number
}

export interface MatchProfile {
  home_team: string
  away_team: string
  home_form: string[]
  away_form: string[]
  // Real - null when there's no prior real match to compute from,
  // never a guessed default. See backend app/knowledge/rest_days.py.
  rest_days_home: number | null
  rest_days_away: number | null
  head_to_head: HeadToHead
}

export type EvidenceSupports = 'HOME' | 'AWAY'

export interface Evidence {
  title: string
  supports: EvidenceSupports
  strength: number
  reason: string
}

export type PredictionWinner = 'HOME' | 'AWAY' | 'DRAW'

export interface ReasoningResult {
  home_team: string
  away_team: string
  strengths: string[]
  weaknesses: string[]
  risks: string[]
  opportunities: string[]
  contradictions: string[]
  summary: string
  supporting_evidence: Evidence[]
}

/** How genuinely the evidence disagrees with itself. */
export type ConflictLevel = 'NONE' | 'LOW' | 'MODERATE' | 'HIGH'

export interface PredictionResult {
  winner: PredictionWinner
  /**
   * The probability of `winner` specifically - always equal to
   * whichever of the three below matches it. It used to be a
   * home-lean index reported for every outcome, so an away pick
   * displayed the home team's number.
   */
  probability: number
  home_probability: number
  draw_probability: number
  away_probability: number
  confidence: number
  market: string
  /** Strongest signal behind the call, ranked by evidence strength. */
  strongest_support: Evidence | null
  /** Strongest signal against it. */
  strongest_opposition: Evidence | null
  conflict: ConflictLevel
  reasoning: ReasoningResult
  explanation: string[]
  summary: string
}

export type CompetitionAvailability = 'ACTIVE' | 'NO_UPCOMING_FIXTURES' | 'EMPTY'

export interface Competition {
  name: string
  season: number | null
  availability: CompetitionAvailability
  total_matches: number
  played_matches: number
  upcoming_matches: number
  next_kickoff: string | null
  last_kickoff: string | null
  prediction_ready: boolean
}
