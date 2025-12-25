// services/JobService.ts - Service mis à jour

import type { 
  JobOffer, 
  JobOfferCreate, 
  JobFilters, 
  PaginatedResponse,
  JobMatchingConfig,
  MatchingConfigResponse,
  MatchingWeights
} from "../types/api"
import { apiClient } from "./apiClient"

class JobService {
  async getJobs(filters?: JobFilters): Promise<PaginatedResponse<JobOffer>> {
    try {
      const params = new URLSearchParams()

      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== "") {
            params.append(key, value.toString())
          }
        })
      }

      const queryString = params.toString()
      const endpoint = `/api/recruitment/jobs/${queryString ? `?${queryString}` : ""}`

      const response = await apiClient.get<PaginatedResponse<JobOffer>>(endpoint)
      return response
    } catch (error: any) {
      console.error("[JobService] Error fetching jobs:", error)
      return {
        results: [],
        count: 0,
        next: null,
        previous: null,
      }
    }
  }

  async getJob(id: number): Promise<JobOffer> {
    const response = await apiClient.get<JobOffer>(`/api/recruitment/jobs/${id}/`)
    return response
  }

  async createJob(data: JobOfferCreate): Promise<JobOffer> {
    const response = await apiClient.post<JobOffer>("/api/recruitment/jobs/", data)
    return response
  }

  async updateJob(id: number, data: Partial<JobOfferCreate>): Promise<JobOffer> {
    const response = await apiClient.patch<JobOffer>(`/api/recruitment/jobs/${id}/`, data)
    return response
  }

  async deleteJob(id: number): Promise<void> {
    await apiClient.delete(`/api/recruitment/jobs/${id}/`)
  }

  async duplicateJob(id: number): Promise<JobOffer> {
    const response = await apiClient.post<JobOffer>(`/api/recruitment/jobs/${id}/duplicate/`)
    return response
  }

  // ===== NOUVEAUX ENDPOINTS POUR LE MATCHING PERSONNALISÉ =====
  
  async getMatchingConfig(id: number): Promise<MatchingConfigResponse> {
    const response = await apiClient.get<MatchingConfigResponse>(`/api/recruitment/jobs/${id}/matching_config/`)
    return response
  }

  async updateMatchingConfig(
    id: number, 
    config: { 
      matching_weights?: MatchingWeights
      system_prompt?: string 
    }
  ): Promise<MatchingConfigResponse> {
    const response = await apiClient.patch<MatchingConfigResponse>(
      `/api/recruitment/jobs/${id}/matching_config/`, 
      config
    )
    return response
  }

  async resetMatchingConfig(id: number): Promise<MatchingConfigResponse> {
    const response = await apiClient.post<MatchingConfigResponse>(`/api/recruitment/jobs/${id}/reset_matching_config/`)
    return response
  }

  async findMatchingCandidates(
    id: number, 
    options: {
      top_n?: number
      min_score?: number
      exclude_applied?: boolean
      use_custom_config?: boolean
    } = {}
  ): Promise<any> {
    const response = await apiClient.post(
      `/api/recruitment/jobs/${id}/find_matching_candidates/`, 
      {
        top_n: options.top_n || 15,
        min_score: options.min_score || 0.0,
        exclude_applied: options.exclude_applied !== false,
        use_custom_config: options.use_custom_config !== false
      }
    )
    return response
  }

  async invalidateMatchingCache(id: number): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post(`/api/recruitment/jobs/${id}/invalidate_cache/`)
    return response
  }
}

export default new JobService()