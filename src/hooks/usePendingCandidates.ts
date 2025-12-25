import { useState, useEffect } from "react"
import candidateService from "../services/candidateService"
import type { BulkUploadResult, PendingCandidate, UploadResponse } from "../types/api"

export const usePendingCandidates = () => {
  const [pendingCandidates, setPendingCandidates] = useState<PendingCandidate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState({
    current_page: 1,
    total_pages: 1,
    total_count: 0,
    has_next: false,
    has_previous: false
  })

  const fetchPendingCandidates = async (page = 1) => {
    try {
      setLoading(true)
      setError(null)
      const response = await candidateService.getPendingCandidates(page)
      
      if (response.success) {
        setPendingCandidates(response.candidates)
        setPagination(response.pagination)
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const uploadCV = async (file: File): Promise<UploadResponse> => {
    try {
      const response = await candidateService.uploadSingleCV(file)
      if (response.success) {
        await fetchPendingCandidates()
      }
      return response
    } catch (error: unknown) {
      throw error instanceof Error ? error : new Error('Upload failed')
    }
  }

  const bulkUploadCVs = async (files: FileList): Promise<BulkUploadResult> => {
    try {
      const response = await candidateService.bulkUploadCVs(files)
      if (response.success) {
        await fetchPendingCandidates()
      }
      return response
    } catch (error: unknown) {
      throw error instanceof Error ? error : new Error('Bulk upload failed')
    }
  }

  const extractCandidate = async (candidateId: number): Promise<any> => {
    try {
      const response = await candidateService.extractCVData(candidateId)
      if (response.success) {
        // Recharger la liste après extraction
        await fetchPendingCandidates()
      }
      return response
    } catch (error: any) {
      throw error
    }
  }

  useEffect(() => {
    fetchPendingCandidates()
  }, [])

  return {
    pendingCandidates,
    loading,
    error,
    pagination,
    fetchPendingCandidates,
    uploadCV,
    bulkUploadCVs,
    extractCandidate,
    refetch: () => fetchPendingCandidates()
  }
}