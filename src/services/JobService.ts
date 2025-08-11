import apiClient from './apiClient'
import { API_BASE_URL, API_ENDPOINTS } from '../config/api'
import axios from 'axios'
import type { JobOffer, JobOfferCreate, PaginatedResponse, JobFilters } from '../types/api'

class JobService {
  // Récupérer toutes les offres d'emploi
  async getJobs(filters?: JobFilters): Promise<PaginatedResponse<JobOffer>> {
    try {
      const params = new URLSearchParams()
      
      if (filters?.status) params.append('status', filters.status)
      if (filters?.experience_level) params.append('experience_level', filters.experience_level)
      if (filters?.location) params.append('location', filters.location)
      if (filters?.search) params.append('search', filters.search)
      if (filters?.page) params.append('page', filters.page.toString())

      const response = await apiClient.get(`${API_ENDPOINTS.JOBS}?${params.toString()}`)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la récupération des offres')
    }
  }

  // Récupérer une offre d'emploi par ID
  async getJob(id: number): Promise<JobOffer> {
    try {
      const response = await apiClient.get(API_ENDPOINTS.JOB_DETAIL(id))
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la récupération de l\'offre')
    }
  }

  // Créer une nouvelle offre d'emploi
  async createJob(jobData: JobOfferCreate): Promise<JobOffer> {
    try {
      const response = await apiClient.post(API_ENDPOINTS.JOBS, jobData)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la création de l\'offre')
    }
  }

  // Mettre à jour une offre d'emploi
  async updateJob(id: number, jobData: Partial<JobOfferCreate>): Promise<JobOffer> {
    try {
      const response = await apiClient.patch(API_ENDPOINTS.JOB_DETAIL(id), jobData)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la mise à jour de l\'offre')
    }
  }

  // Supprimer une offre d'emploi
  async deleteJob(id: number): Promise<void> {
    try {
      await apiClient.delete(API_ENDPOINTS.JOB_DETAIL(id))
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la suppression de l\'offre')
    }
  }

  // Générer des questions d'entretien avec IA
  async generateQuestions(jobId: number): Promise<any> {
    try {
      const response = await apiClient.post(API_ENDPOINTS.JOB_QUESTIONS(jobId))
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la génération des questions')
    }
  }

  // Trouver des candidats compatibles
  async findMatchingCandidates(jobId: number): Promise<any> {
    try {
      const response = await apiClient.get(API_ENDPOINTS.JOB_MATCHING(jobId))
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur lors de la recherche de candidats')
    }
  }
}

export default new JobService()
