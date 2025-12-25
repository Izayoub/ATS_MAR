import { apiClient } from "./apiClient"
import { API_ENDPOINTS } from "../config/api"
import type { CandidateGroup,CandidateGroupCreate,CandidateGroupFilters,GroupAnalytics,BulkActionRequest,BulkActionResponse } from "../types/api";

// Types pour les groupes

class CandidateGroupService {
  async getGroups(filters?: CandidateGroupFilters): Promise<{ results: CandidateGroup[], count: number }> {
    try {
      const params = new URLSearchParams()
      
      if (filters?.search) params.append("search", filters.search)
      if (filters?.type_groupe) params.append("type_groupe", filters.type_groupe)
      if (filters?.is_active !== undefined) params.append("is_active", filters.is_active.toString())
      if (filters?.candidat_id) params.append("candidat_id", filters.candidat_id.toString())
      if (filters?.ordering) params.append("ordering", filters.ordering)
      if (filters?.page) params.append("page", filters.page.toString())

      const queryString = params.toString()
      const url = queryString ? `${API_ENDPOINTS.CANDIDATE_GROUPS}?${queryString}` : API_ENDPOINTS.CANDIDATE_GROUPS

      const response = await apiClient.get<{ results: CandidateGroup[], count: number }>(url)
      return response
    } catch (error) {
      console.error("Error fetching candidate groups:", error)
      return { results: [], count: 0 }
    }
  }

  async getGroupsSummary(): Promise<CandidateGroup[]> {
    try {
      const response = await apiClient.get<{ success: boolean, groupes: CandidateGroup[] }>(
        `${API_ENDPOINTS.CANDIDATE_GROUPS}list_summary/`
      )
      return response.groupes || []
    } catch (error) {
      console.error("Error fetching groups summary:", error)
      return []
    }
  }

  async getGroupById(id: number): Promise<CandidateGroup> {
    return await apiClient.get<CandidateGroup>(`${API_ENDPOINTS.CANDIDATE_GROUPS}${id}/`)
  }

  async createGroup(data: CandidateGroupCreate): Promise<CandidateGroup> {
    return await apiClient.post<CandidateGroup>(API_ENDPOINTS.CANDIDATE_GROUPS, data)
  }

  async updateGroup(id: number, data: Partial<CandidateGroupCreate>): Promise<CandidateGroup> {
    return await apiClient.patch<CandidateGroup>(`${API_ENDPOINTS.CANDIDATE_GROUPS}${id}/`, data)
  }

  async deleteGroup(id: number): Promise<void> {
    await apiClient.delete(`${API_ENDPOINTS.CANDIDATE_GROUPS}${id}/`)
  }

  async addCandidatesToGroup(groupId: number, candidateIds: number[]): Promise<{
    success: boolean
    added_count: number
    already_in_group: string[]
    total_candidats: number
  }> {
    return await apiClient.post(
      `${API_ENDPOINTS.CANDIDATE_GROUPS}${groupId}/add_candidats/`,
      { candidat_ids: candidateIds }
    )
  }

  async removeCandidatesFromGroup(groupId: number, candidateIds: number[]): Promise<{
    success: boolean
    removed_count: number
    not_in_group: string[]
    total_candidats: number
  }> {
    return await apiClient.post(
      `${API_ENDPOINTS.CANDIDATE_GROUPS}${groupId}/remove_candidats/`,
      { candidat_ids: candidateIds }
    )
  }

  async syncGroupWithCriteria(groupId: number): Promise<{
    success: boolean
    added_count: number
    total_candidats: number
    last_sync: string
    criteria_applied: any
  }> {
    return await apiClient.post(`${API_ENDPOINTS.CANDIDATE_GROUPS}${groupId}/sync_auto_criteria/`)
  }

  async getGroupAnalytics(groupId: number): Promise<{
    success: boolean
    groupe: {
      id: number
      nom: string
      type_groupe: string
      couleur: string
    }
    analytics: GroupAnalytics
    generated_at: string
  }> {
    return await apiClient.get(`${API_ENDPOINTS.CANDIDATE_GROUPS}${groupId}/analytics/`)
  }

  async bulkActions(request: BulkActionRequest): Promise<BulkActionResponse> {
    return await apiClient.post(`${API_ENDPOINTS.CANDIDATE_GROUPS}bulk_actions/`, request)
  }

  // Méthodes utilitaires
  getGroupColorValue(color: CandidateGroup["couleur"]): string {
    const colorMap = {
      blue: "#3b82f6",
      green: "#10b981", 
      red: "#ef4444",
      yellow: "#f59e0b",
      purple: "#8b5cf6",
      orange: "#f97316",
      gray: "#6b7280",
      teal: "#14b8a6"
    }
    return colorMap[color] || colorMap.blue
  }

  getGroupTypeLabel(type: CandidateGroup["type_groupe"]): string {
    const typeMap = {
      competence: "Par compétence",
      experience: "Par expérience", 
      projet: "Par projet",
      pipeline: "Pipeline de recrutement",
      performance: "Par performance",
      geographic: "Par zone géographique",
      custom: "Personnalisé"
    }
    return typeMap[type] || "Personnalisé"
  }
}

const candidateGroupService = new CandidateGroupService()
export default candidateGroupService