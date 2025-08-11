import apiClient from './apiClient'
import { API_ENDPOINTS } from '../config/api'
import type { Candidate, PaginatedResponse, CandidateFilters } from '../types/api'

class CandidateService {
  // Récupérer tous les candidats
  async getCandidates(filters?: CandidateFilters): Promise<PaginatedResponse<Candidate>> {
    try {
      const params = new URLSearchParams()
      
      if (filters?.city) params.append('city', filters.city)
      if (filters?.experience_years) params.append('experience_years', filters.experience_years.toString())
      if (filters?.skills) params.append('skills', filters.skills)
      if (filters?.search) params.append('search', filters.search)
      if (filters?.page) params.append('page', filters.page.toString())

      const response = await apiClient.get(`${API_ENDPOINTS.CANDIDATES}?${params.toString()}`)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la récupération des candidats')
    }
  }

  // Récupérer un candidat par ID
  async getCandidate(id: number): Promise<Candidate> {
    try {
      const response = await apiClient.get(API_ENDPOINTS.CANDIDATE_DETAIL(id))
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la récupération du candidat')
    }
  }

  // Upload et parsing de CV
  async uploadCV(formData: FormData): Promise<any> {
    try {
      const response = await apiClient.post(API_ENDPOINTS.CANDIDATE_UPLOAD, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de l\'upload du CV')
    }
  }

  // Re-parser un CV existant
  async reparseCV(candidateId: number): Promise<any> {
    try {
      const response = await apiClient.post(API_ENDPOINTS.CANDIDATE_REPARSE(candidateId))
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors du re-parsing du CV')
    }
  }

  // Mettre à jour un candidat
  async updateCandidate(id: number, candidateData: Partial<Candidate>): Promise<Candidate> {
    try {
      const response = await apiClient.patch(API_ENDPOINTS.CANDIDATE_DETAIL(id), candidateData)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la mise à jour du candidat')
    }
  }

  // Supprimer un candidat
  async deleteCandidate(id: number): Promise<void> {
    try {
      await apiClient.delete(API_ENDPOINTS.CANDIDATE_DETAIL(id))
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la suppression du candidat')
    }
  }
}

export default new CandidateService()
