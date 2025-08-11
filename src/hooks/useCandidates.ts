import { useState, useEffect } from 'react'
import candidateService from '../services/candidateService'
import type { Candidate, CandidateFilters, PaginatedResponse } from '../types/api'

export const useCandidates = (filters?: CandidateFilters) => {
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState<{
  count: number
  next: string | null
  previous: string | null
}>({
  count: 0,
  next: null,
  previous: null,
})

  const fetchCandidates = async (newFilters?: CandidateFilters) => {
    try {
      setLoading(true)
      setError(null)
      const response: PaginatedResponse<Candidate> = await candidateService.getCandidates(newFilters || filters)
      setCandidates(response.results)
      setPagination({
        count: response.count,
        next: response.next || null,
        previous: response.previous || null,
      })
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCandidates()
  }, [])

  const refetch = (newFilters?: CandidateFilters) => {
    fetchCandidates(newFilters)
  }

  return {
    candidates,
    loading,
    error,
    pagination,
    refetch,
  }
}
