import { useState, useEffect } from 'react'
import jobService from '../services/JobService'
import type { JobOffer, JobFilters, PaginatedResponse } from '../types/api'
import { useNavigate } from 'react-router-dom'

export const useJobs = (filters?: JobFilters) => {
  const [jobs, setJobs] = useState<JobOffer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const [pagination, setPagination] = useState<{
  count: number
  next: string | null
  previous: string | null
}>({
  count: 0,
  next: null,
  previous: null,
})

  const fetchJobs = async (newFilters?: JobFilters) => {
    try {
      setLoading(true)
      setError(null)
      const response: PaginatedResponse<JobOffer> = await jobService.getJobs(newFilters || filters)
      setJobs(response.results)
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
    fetchJobs()
  }, [])

  const refetch = (newFilters?: JobFilters) => {
    fetchJobs(newFilters)
  }

  return {
    jobs,
    loading,
    error,
    pagination,
    refetch,
  }
}
