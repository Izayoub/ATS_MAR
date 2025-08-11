import apiClient from './apiClient'
import { API_ENDPOINTS } from '../config/api'
import type { Application, PaginatedResponse } from '../types/api'

class ApplicationService {
  // Récupérer toutes les candidatures
  async getApplications(filters?: any): Promise<PaginatedResponse<Application>> {
    try {
      const params = new URLSearchParams()
      
      if (filters?.status) params.append('status', filters.status)
      if (filters?.job_offer) params.append('job_offer', filters.job_offer.toString())
      if (filters?.source) params.append('source', filters.source)
      if (filters?.page) params.append('page', filters.page.toString())

      const response = await apiClient.get(`${API_ENDPOINTS.APPLICATIONS}?${params.toString()}`)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la récupération des candidatures')
    }
  }

  // Créer une candidature
  async createApplication(applicationData: any): Promise<any> {
    try {
      const response = await apiClient.post(API_ENDPOINTS.APPLICATION_CREATE, applicationData)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la création de la candidature')
    }
  }

  // Mettre à jour le statut d'une candidature
  async updateApplicationStatus(id: number, status: string): Promise<any> {
    try {
      const response = await apiClient.post(API_ENDPOINTS.APPLICATION_STATUS(id), { status })
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la mise à jour du statut')
    }
  }

  // Récupérer les statistiques du pipeline
  async getPipelineStats(): Promise<any> {
    try {
      const response = await apiClient.get(API_ENDPOINTS.PIPELINE_STATS)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la récupération des statistiques')
    }
  }
}

export default new ApplicationService()
