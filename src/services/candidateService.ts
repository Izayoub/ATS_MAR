import { apiClient } from "./apiClient"
import { API_ENDPOINTS } from "../config/api"
import type {
  Candidate,
  CandidateFilters,
  PaginatedResponse,
  CandidateNote,
  TimelineEvent,
  JobMatch,
  PendingCandidate,
  UploadResponse,
  BulkUploadResult,
} from "../types/api"

class CandidateService {
  async getCandidates(filters?: CandidateFilters): Promise<PaginatedResponse<Candidate>> {
    try {
      const params = new URLSearchParams()

      if (filters?.search) params.append("search", filters.search)
      if (filters?.status) params.append("status", filters.status)
      if (filters?.skills?.length) params.append("skills", filters.skills.join(","))
      if (filters?.experience_min) params.append("experience_min", filters.experience_min.toString())
      if (filters?.experience_max) params.append("experience_max", filters.experience_max.toString())
      if (filters?.location) params.append("location", filters.location)
      if (filters?.page) params.append("page", filters.page.toString())
      if (filters?.page_size) params.append("page_size", filters.page_size.toString())

      const queryString = params.toString()
      const url = queryString ? `${API_ENDPOINTS.CANDIDATES}?${queryString}` : API_ENDPOINTS.CANDIDATES

      const response = await apiClient.get<PaginatedResponse<Candidate>>(url)
      return response
    } catch (error) {
      console.error("Error fetching candidates:", error)
      // Return empty paginated response on error
      return {
        count: 0,
        next: null,
        previous: null,
        results: [],
      }
    }
  }

  async getCandidateById(id: number): Promise<Candidate> {
    return await apiClient.get<Candidate>(API_ENDPOINTS.CANDIDATE_DETAIL(id))
  }

  async getCandidateNotes(id: number): Promise<CandidateNote[]> {
    try {
      const response = await apiClient.get<CandidateNote[]>(`${API_ENDPOINTS.CANDIDATE_DETAIL(id)}notes/`)
      return response || []
    } catch (error) {
      console.error("Error fetching candidate notes:", error)
      return []
    }
  }

  async getCandidateTimeline(id: number): Promise<TimelineEvent[]> {
    try {
      const response = await apiClient.get<TimelineEvent[]>(`${API_ENDPOINTS.CANDIDATE_DETAIL(id)}timeline/`)
      return response || []
    } catch (error) {
      console.error("Error fetching candidate timeline:", error)
      return []
    }
  }

  async findMatchingJobs(id: number): Promise<{ matches: JobMatch[] }> {
    try {
      const response = await apiClient.get<{ matches: JobMatch[] }>(API_ENDPOINTS.CANDIDATE_MATCHING(id))
      return response || { matches: [] }
    } catch (error) {
      console.error("Error finding matching jobs:", error)
      return { matches: [] }
    }
  }

  async updateCandidateStatus(id: number, status: Candidate["status"]): Promise<Candidate> {
    return await apiClient.patch<Candidate>(API_ENDPOINTS.CANDIDATE_DETAIL(id), { status })
  }

  async addCandidateNote(id: number, content: string, noteType = "note"): Promise<CandidateNote> {
    return await apiClient.post<CandidateNote>(`${API_ENDPOINTS.CANDIDATE_DETAIL(id)}notes/`, {
      content,
      note_type: noteType,
    })
  }

  async deleteCandidate(id: number): Promise<void> {
    await apiClient.delete(`${API_ENDPOINTS.CANDIDATE_DETAIL(id)}`)
  }

  async uploadSingleCV(file: File): Promise<UploadResponse> {
    try {
      const formData = new FormData()
      formData.append("cv_file", file)

      // Fixed: Removed the config object as third parameter
      const response = await apiClient.post<UploadResponse>(API_ENDPOINTS.CANDIDATE_UPLOAD_CV, formData)
      return response
    } catch (error: any) {
      throw new Error(error.response?.data?.error || "Erreur lors de l'upload du CV")
    }
  }

  async bulkUploadCVs(files: FileList): Promise<BulkUploadResult> {
    try {
      const formData = new FormData()
      Array.from(files).forEach((file) => {
        formData.append("cv_files", file)
      })

      // Fixed: Added explicit type parameter
      const response = await apiClient.post<{
        success: boolean
        uploaded_count: number
        error_count: number
        results: Array<{
          candidate_id: number
          filename: string
          cv_file_url: string
          status: string
        }>
        errors: string[]
      }>(API_ENDPOINTS.CANDIDATE_BULK_UPLOAD, formData)
      return response
    } catch (error: any) {
      throw new Error(error.response?.data?.error || "Erreur lors de l'upload en lot")
    }
  }

  async getPendingCandidates(page = 1): Promise<{
    success: boolean
    candidates: PendingCandidate[]
    pagination: {
      current_page: number
      total_pages: number
      total_count: number
      has_next: boolean
      has_previous: boolean
    }
  }> {
    try {
      const params = new URLSearchParams()
      params.append("page", page.toString())

      const url = `${API_ENDPOINTS.CANDIDATE_PENDING_EXTRACTION}?${params.toString()}`
      const response = await apiClient.get<{
        success: boolean
        candidates: PendingCandidate[]
        pagination: {
          current_page: number
          total_pages: number
          total_count: number
          has_next: boolean
          has_previous: boolean
        }
      }>(url)
      return response
    } catch (error: any) {
      console.error("Error fetching pending candidates:", error)
      return {
        success: false,
        candidates: [],
        pagination: {
          current_page: 1,
          total_pages: 0,
          total_count: 0,
          has_next: false,
          has_previous: false,
        },
      }
    }
  }

  async extractCVData(candidateId: number): Promise<{
    success: boolean
    message: string
    candidate_id: number
    cv_file_path: string
  }> {
    try {
      const response = await apiClient.post<{
        success: boolean
        message: string
        candidate_id: number
        cv_file_path: string
      }>(API_ENDPOINTS.CANDIDATE_EXTRACT_DATA(candidateId))
      return response
    } catch (error: any) {
      throw new Error(error.response?.data?.error || "Erreur lors de l'extraction")
    }
  }

  // Méthode utilitaire pour valider les fichiers
  validateCVFile(file: File): { isValid: boolean; error?: string } {
    const allowedFormats = [".pdf", ".txt", ".doc", ".docx"]
    const maxSize = 5 * 1024 * 1024 // 5MB

    const fileExtension = "." + file.name.split(".").pop()?.toLowerCase()

    if (!allowedFormats.includes(fileExtension)) {
      return {
        isValid: false,
        error: `Format non supporté. Formats acceptés: ${allowedFormats.join(", ")}`,
      }
    }

    if (file.size > maxSize) {
      return {
        isValid: false,
        error: `Fichier trop volumineux. Taille maximum: 5MB`,
      }
    }

    return { isValid: true }
  }

  // Méthode pour formater la taille des fichiers
  formatFileSize(bytes: number): string {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }
}

const candidateService = new CandidateService()
export default candidateService
