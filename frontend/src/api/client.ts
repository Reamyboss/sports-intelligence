const BASE_URL = import.meta.env.VITE_API_BASE_URL

/**
 * Thrown for any non-2xx response. `status` lets callers distinguish
 * "not found" from "the backend errored" from "we couldn't reach the
 * backend at all" (status 0).
 */
export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  let response: Response

  try {
    response = await fetch(`${BASE_URL}${path}`)
  } catch {
    throw new ApiError('Could not reach the backend.', 0)
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`

    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') {
        detail = body.detail
      }
    } catch {
      // response had no JSON body - keep the generic message
    }

    throw new ApiError(detail, response.status)
  }

  return response.json() as Promise<T>
}
