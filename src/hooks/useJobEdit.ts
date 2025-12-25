// hooks/useJobEdit.ts - Hook mis à jour avec matching config

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import jobService from "../services/JobService"
import { useToast } from "../contexts/ToastContext"
import type { JobOffer, JobOfferCreate, MatchingWeights } from "../types/api"

interface UseJobEditOptions {
  id?: string
  onSuccess?: (job: JobOffer) => void
  onError?: (error: string) => void
}

export interface JobEditFormData {
  title: string
  description: string
  requirements: string[]
  benefits: string[]
  status: "draft" | "active" | "paused" | "closed"
  experience_level: "junior" | "middle" | "senior"
  remote_allowed: boolean
  contract_type: string
  deadline: string
  
  // Nouveaux champs pour le matching personnalisé
  matching_weights?: MatchingWeights
  system_prompt?: string
}

export const useJobEdit = (options: UseJobEditOptions = {}) => {
  const { id, onSuccess, onError } = options
  const { addToast } = useToast()
  const navigate = useNavigate()

  const [formData, setFormData] = useState<JobEditFormData>({
    title: "",
    description: "",
    requirements: [],
    benefits: [],
    status: "draft",
    experience_level: "middle",
    remote_allowed: false,
    contract_type: "CDI",
    deadline: "",
    matching_weights: undefined,
    system_prompt: undefined,
  })

  const [originalJob, setOriginalJob] = useState<JobOffer | null>(null)
  const [loading, setLoading] = useState(!!id)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState<Partial<JobEditFormData>>({})

  // Charger les données de l'offre existante
  useEffect(() => {
    if (id) {
      loadJob()
    }
  }, [id])

  const loadJob = async () => {
    if (!id) return

    setLoading(true)
    try {
      const jobData = await jobService.getJob(Number(id))
      setOriginalJob(jobData)

      // Convertir les données pour le formulaire
      const requirementsList =
        typeof jobData.requirements === "string"
          ? jobData.requirements.split("\n").filter((req) => req.trim())
          : Array.isArray(jobData.requirements)
            ? jobData.requirements
            : []

      const benefitsList =
        typeof jobData.benefits === "string"
          ? jobData.benefits.split("\n").filter((benefit) => benefit.trim())
          : Array.isArray(jobData.benefits)
            ? jobData.benefits
            : []

      const deadlineFormatted = jobData.deadline ? new Date(jobData.deadline).toISOString().split("T")[0] : ""

      setFormData({
        title: jobData.title || "",
        description: jobData.description || "",
        requirements: requirementsList,
        benefits: benefitsList,
        status: jobData.status || "draft",
        experience_level: jobData.experience_level || "middle",
        remote_allowed: jobData.remote_allowed || false,
        contract_type: jobData.contract_type || "CDI",
        deadline: deadlineFormatted,
        matching_weights: jobData.matching_weights,
        system_prompt: jobData.system_prompt,
      })
    } catch (error: any) {
      const errorMessage = error.message || "Erreur lors du chargement de l'offre"
      addToast(errorMessage, "error")
      onError?.(errorMessage)
      navigate("/jobs")
    } finally {
      setLoading(false)
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Partial<JobEditFormData> = {}

    if (!formData.title.trim()) {
      newErrors.title = "Le titre est requis"
    }

    if (!formData.description.trim()) {
      newErrors.description = "La description est requise"
    }

    if (!formData.deadline) {
      newErrors.deadline = "La date limite est requise"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const saveJob = async (status?: "draft" | "active") => {
    const updatedStatus = status || formData.status

    // Valider seulement si on publie
    if ((status === "active" || formData.status === "active") && !validateForm()) {
      addToast("Veuillez corriger les erreurs avant de publier", "error")
      return false
    }

    setSaving(true)
    try {
      // Préparer les données pour l'API
      const apiData: JobOfferCreate = {
        title: formData.title,
        description: formData.description,
        requirements: formData.requirements.join("\n"),
        benefits: formData.benefits.join("\n"),
        status: updatedStatus,
        experience_level: formData.experience_level,
        remote_allowed: formData.remote_allowed,
        contract_type: formData.contract_type,
        deadline: formData.deadline ? new Date(formData.deadline).toISOString() : null,
        
        // Nouveaux champs de matching
        matching_weights: formData.matching_weights,
        system_prompt: formData.system_prompt?.trim() || undefined,
      }

      let savedJob: JobOffer

      if (id) {
        // Mode édition
        savedJob = await jobService.updateJob(Number(id), apiData)
        addToast("Offre mise à jour avec succès !", "success")
      } else {
        // Mode création
        savedJob = await jobService.createJob(apiData)
        addToast("Offre créée avec succès !", "success")
      }

      onSuccess?.(savedJob)
      return savedJob
    } catch (error: any) {
      const errorMessage = error.message || "Erreur lors de la sauvegarde"
      addToast(errorMessage, "error")
      onError?.(errorMessage)
      return false
    } finally {
      setSaving(false)
    }
  }

  const updateField = <K extends keyof JobEditFormData>(field: K, value: JobEditFormData[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }))

    // Effacer l'erreur pour ce champ
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const addToList = (field: "requirements" | "benefits", item: string) => {
    const trimmedItem = item.trim()
    if (!trimmedItem || formData[field].includes(trimmedItem)) {
      return false
    }

    setFormData((prev) => ({
      ...prev,
      [field]: [...prev[field], trimmedItem],
    }))
    return true
  }

  const removeFromList = (field: "requirements" | "benefits", index: number) => {
    setFormData((prev) => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index),
    }))
  }

  const resetForm = () => {
    if (originalJob) {
      // Restaurer les données originales
      loadJob()
    } else {
      // Réinitialiser le formulaire pour création
      setFormData({
        title: "",
        description: "",
        requirements: [],
        benefits: [],
        status: "draft",
        experience_level: "middle",
        remote_allowed: false,
        contract_type: "CDI",
        deadline: "",
        matching_weights: undefined,
        system_prompt: undefined,
      })
    }
    setErrors({})
  }

  const hasChanges = () => {
    if (!originalJob) return true // Nouveau job

    // Comparer avec les données originales
    const currentApiData = {
      title: formData.title,
      description: formData.description,
      requirements: formData.requirements.join("\n"),
      benefits: formData.benefits.join("\n"),
      status: formData.status,
      experience_level: formData.experience_level,
      remote_allowed: formData.remote_allowed,
      contract_type: formData.contract_type,
      deadline: formData.deadline ? new Date(formData.deadline).toISOString() : null,
      matching_weights: formData.matching_weights,
      system_prompt: formData.system_prompt,
    }

    const originalData = {
      title: originalJob.title,
      description: originalJob.description,
      requirements: typeof originalJob.requirements === "string" ? originalJob.requirements : "",
      benefits: typeof originalJob.benefits === "string" ? originalJob.benefits : "",
      status: originalJob.status,
      experience_level: originalJob.experience_level,
      remote_allowed: originalJob.remote_allowed,
      contract_type: originalJob.contract_type,
      deadline: originalJob.deadline,
      matching_weights: originalJob.matching_weights,
      system_prompt: originalJob.system_prompt,
    }

    return JSON.stringify(currentApiData) !== JSON.stringify(originalData)
  }

  // Nouvelle fonction pour mettre à jour la configuration de matching
  const updateMatchingConfig = (config: { matching_weights?: MatchingWeights; system_prompt?: string }) => {
    setFormData(prev => ({
      ...prev,
      matching_weights: config.matching_weights,
      system_prompt: config.system_prompt,
    }))
  }

  return {
    formData,
    setFormData,
    errors,
    loading,
    saving,
    originalJob,

    // Actions
    saveJob,
    validateForm,
    updateField,
    addToList,
    removeFromList,
    resetForm,
    hasChanges,
    updateMatchingConfig,

    // Helpers
    isEditMode: !!id,
    canPublish: formData.title && formData.description,
  }
}