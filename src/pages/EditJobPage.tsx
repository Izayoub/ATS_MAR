"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { useToast } from "../contexts/ToastContext"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { ArrowLeft, Save, Eye, Plus, X, MapPin, DollarSign, Clock, Briefcase, AlertCircle, Loader } from "lucide-react"
import jobService from "../services/JobService"
import type { JobOffer, JobOfferCreate } from "../types/api"

interface JobFormData {
  title: string
  description: string
  requirements: string[]
  benefits: string[]
  status: "draft" | "active" | "paused" | "closed"
  experience_level: "junior" | "middle" | "senior"
  salary_min: string
  salary_max: string
  location: string
  remote_allowed: boolean
  contract_type: string
  deadline: string
}

const EditJobPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(!!id) // Loading seulement si on édite
  const [saving, setSaving] = useState(false)
  const [newRequirement, setNewRequirement] = useState("")
  const [newBenefit, setNewBenefit] = useState("")

  const [formData, setFormData] = useState<JobFormData>({
    title: "",
    description: "",
    requirements: [],
    benefits: [],
    status: "draft",
    experience_level: "middle",
    salary_min: "",
    salary_max: "",
    location: "",
    remote_allowed: false,
    contract_type: "CDI",
    deadline: "",
  })

  const [errors, setErrors] = useState<Partial<JobFormData>>({})
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  useEffect(() => {
    if (id) {
      fetchJob()
    }
  }, [id])

  useEffect(() => {
    // Marquer les changements non sauvegardés
    setHasUnsavedChanges(true)
  }, [formData])

  const fetchJob = async () => {
    if (!id) return
    
    setLoading(true)
    try {
      console.log("Chargement de l'offre:", id)
      const jobData: JobOffer = await jobService.getJob(Number(id))
      console.log("Données reçues:", jobData)
      
      // Conversion des données API vers le format du formulaire
      const requirementsList = Array.isArray(jobData.requirements) 
        ? jobData.requirements
        : typeof jobData.requirements === 'string' 
          ? jobData.requirements.split('\n').filter(req => req.trim())
          : []

      const benefitsList = Array.isArray(jobData.benefits)
        ? jobData.benefits
        : typeof jobData.benefits === 'string'
          ? jobData.benefits.split('\n').filter(benefit => benefit.trim())
          : []

      // Formatage de la date pour l'input date
      let deadlineFormatted = ""
      if (jobData.deadline) {
        try {
          const date = new Date(jobData.deadline)
          deadlineFormatted = date.toISOString().split('T')[0]
        } catch (e) {
          console.warn("Erreur de formatage de date:", jobData.deadline)
        }
      }

      setFormData({
        title: jobData.title || "",
        description: jobData.description || "",
        requirements: requirementsList,
        benefits: benefitsList,
        status: jobData.status || "draft",
        experience_level: jobData.experience_level || "middle",
        salary_min: jobData.salary_min?.toString() || "",
        salary_max: jobData.salary_max?.toString() || "",
        location: jobData.location || "",
        remote_allowed: jobData.remote_allowed || false,
        contract_type: jobData.contract_type || "CDI",
        deadline: deadlineFormatted,
      })

      setHasUnsavedChanges(false) // Pas de changements après chargement
      addToast("Offre chargée avec succès", "success")
    } catch (error: any) {
      console.error("Erreur lors du chargement:", error)
      addToast(error.message || "Erreur lors du chargement de l'offre", "error")
      // Redirection seulement si l'offre n'existe pas
      if (error.message?.includes('404') || error.message?.includes('introuvable')) {
        navigate("/jobs")
      }
    } finally {
      setLoading(false)
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Partial<JobFormData> = {}

    // Validations obligatoires
    if (!formData.title.trim()) {
      newErrors.title = "Le titre est requis"
    }
    
    if (!formData.location.trim()) {
      newErrors.location = "La localisation est requise"
    }
    
    if (!formData.description.trim()) {
      newErrors.description = "La description est requise"
    }

    // Validations pour publication
    if (formData.status === "active") {
      if (!formData.deadline) {
        newErrors.deadline = "La date limite est requise pour publier"
      }
      
      if (!formData.salary_min) {
        newErrors.salary_min = "Le salaire minimum est requis pour publier"
      }
      
      if (!formData.salary_max) {
        newErrors.salary_max = "Le salaire maximum est requis pour publier"
      }

      // Validation de cohérence des salaires
      if (formData.salary_min && formData.salary_max) {
        const minSalary = Number.parseFloat(formData.salary_min)
        const maxSalary = Number.parseFloat(formData.salary_max)
        
        if (isNaN(minSalary) || isNaN(maxSalary)) {
          if (isNaN(minSalary)) newErrors.salary_min = "Salaire minimum invalide"
          if (isNaN(maxSalary)) newErrors.salary_max = "Salaire maximum invalide"
        } else if (minSalary >= maxSalary) {
          newErrors.salary_max = "Le salaire maximum doit être supérieur au minimum"
        } else if (minSalary < 0) {
          newErrors.salary_min = "Le salaire ne peut pas être négatif"
        }
      }

      // Validation de la date limite
      if (formData.deadline) {
        const deadlineDate = new Date(formData.deadline)
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        
        if (deadlineDate < today) {
          newErrors.deadline = "La date limite ne peut pas être dans le passé"
        }
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (targetStatus?: "draft" | "active") => {
    const statusToSave = targetStatus || formData.status

    // Mise à jour du statut si spécifié
    const dataToValidate = targetStatus 
      ? { ...formData, status: targetStatus }
      : formData

    // Validation selon le statut cible
    const tempFormData = formData
    if (targetStatus) {
      setFormData({ ...formData, status: targetStatus })
    }

    if (!validateForm()) {
      if (targetStatus) {
        setFormData(tempFormData) // Restaurer l'état précédent
      }
      addToast("Veuillez corriger les erreurs avant de continuer", "error")
      return
    }

    setSaving(true)
    try {
      // Préparation des données pour l'API
      const apiData: JobOfferCreate = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        requirements: formData.requirements.join('\n'),
        benefits: formData.benefits.join('\n'),
        status: statusToSave,
        experience_level: formData.experience_level,
        salary_min: formData.salary_min ? Number.parseFloat(formData.salary_min) : null,
        salary_max: formData.salary_max ? Number.parseFloat(formData.salary_max) : null,
        location: formData.location.trim(),
        remote_allowed: formData.remote_allowed,
        contract_type: formData.contract_type,
        deadline: formData.deadline ? new Date(formData.deadline + 'T23:59:59Z').toISOString() : null,
      }

      console.log("Données à envoyer:", apiData)

      let savedJob: JobOffer

      if (id) {
        // Mode édition
        savedJob = await jobService.updateJob(Number(id), apiData)
        addToast("Offre mise à jour avec succès !", "success")
        console.log("Offre mise à jour:", savedJob)
      } else {
        // Mode création
        savedJob = await jobService.createJob(apiData)
        addToast("Offre créée avec succès !", "success")
        console.log("Offre créée:", savedJob)
      }

      // Mise à jour du statut dans le state
      if (targetStatus) {
        setFormData(prev => ({ ...prev, status: targetStatus }))
      }
      
      setHasUnsavedChanges(false)

      // Redirection après succès
      setTimeout(() => {
        navigate(`/jobs/${savedJob.id}`)
      }, 1000)

    } catch (error: any) {
      console.error("Erreur lors de la sauvegarde:", error)
      
      // Restaurer l'état précédent en cas d'erreur
      if (targetStatus) {
        setFormData(tempFormData)
      }
      
      let errorMessage = "Erreur lors de la sauvegarde"
      
      if (error.message) {
        errorMessage = error.message
      } else if (error.response?.data) {
        const errorData = error.response.data
        if (typeof errorData === 'string') {
          errorMessage = errorData
        } else if (errorData.detail) {
          errorMessage = errorData.detail
        } else if (errorData.error) {
          errorMessage = errorData.error
        }
      }
      
      addToast(errorMessage, "error")
    } finally {
      setSaving(false)
    }
  }

  const addRequirement = () => {
    const trimmed = newRequirement.trim()
    if (trimmed && !formData.requirements.includes(trimmed)) {
      setFormData({
        ...formData,
        requirements: [...formData.requirements, trimmed],
      })
      setNewRequirement("")
    }
  }

  const removeRequirement = (index: number) => {
    setFormData({
      ...formData,
      requirements: formData.requirements.filter((_, i) => i !== index),
    })
  }

  const addBenefit = () => {
    const trimmed = newBenefit.trim()
    if (trimmed && !formData.benefits.includes(trimmed)) {
      setFormData({
        ...formData,
        benefits: [...formData.benefits, trimmed],
      })
      setNewBenefit("")
    }
  }

  const removeBenefit = (index: number) => {
    setFormData({
      ...formData,
      benefits: formData.benefits.filter((_, i) => i !== index),
    })
  }

  const updateFormField = <K extends keyof JobFormData>(
    field: K,
    value: JobFormData[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Effacer l'erreur pour ce champ
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const locations = [
    "Casablanca", "Rabat", "Marrakech", "Fès", "Tanger", "Agadir",
    "Meknès", "Oujda", "Télétravail", "Hybride"
  ]

  const experienceLevels = [
    { value: "junior", label: "Junior (0-2 ans)" },
    { value: "middle", label: "Confirmé (2-5 ans)" },
    { value: "senior", label: "Senior (5+ ans)" },
  ]

  const contractTypes = [
    { value: "CDI", label: "CDI" },
    { value: "CDD", label: "CDD" },
    { value: "Stage", label: "Stage" },
    { value: "Freelance", label: "Freelance" },
  ]

  const statusOptions = [
    { value: "draft", label: "Brouillon", color: "gray" },
    { value: "active", label: "Active", color: "green" },
    { value: "paused", label: "En pause", color: "yellow" },
    { value: "closed", label: "Fermée", color: "red" },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-purple-600" />
          <p className="text-gray-600">Chargement de l'offre...</p>
        </div>
      </div>
    )
  }

  const isEditMode = !!id
  const canPublish = formData.title && formData.description && formData.location

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button 
              variant="outline" 
              onClick={() => navigate(id ? `/jobs/${id}` : "/jobs")} 
              className="flex items-center"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Retour
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                {isEditMode ? "Modifier l'offre" : "Créer une offre"}
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                {isEditMode ? "Mettez à jour les informations de l'offre" : "Créez une nouvelle offre d'emploi"}
              </p>
              {hasUnsavedChanges && (
                <p className="text-orange-500 text-sm mt-1">
                  ⚠️ Modifications non sauvegardées
                </p>
              )}
            </div>
          </div>
          
          <div className="flex space-x-3">
            <Button 
              variant="outline" 
              onClick={() => handleSubmit("draft")} 
              disabled={saving}
              className="min-w-[140px]"
            >
              {saving ? (
                <><Loader className="w-4 h-4 mr-2 animate-spin" />Sauvegarde...</>
              ) : (
                <><Save className="w-4 h-4 mr-2" />Sauvegarder</>
              )}
            </Button>
            
            <Button
              onClick={() => handleSubmit("active")}
              disabled={saving || !canPublish}
              className="bg-green-600 hover:bg-green-700 min-w-[140px]"
              title={!canPublish ? "Veuillez remplir les champs obligatoires" : ""}
            >
              {saving ? (
                <><Loader className="w-4 h-4 mr-2 animate-spin" />Publication...</>
              ) : (
                <><Eye className="w-4 h-4 mr-2" />{formData.status === "active" ? "Mettre à jour" : "Publier"}</>
              )}
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Formulaire principal */}
          <div className="lg:col-span-2 space-y-6">
            {/* Informations générales */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center text-gray-900 dark:text-white">
                  <Briefcase className="w-5 h-5 mr-2" />
                  Informations générales
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Titre du poste *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => updateFormField('title', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors ${
                      errors.title ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                    }`}
                    placeholder="Ex: Développeur Full Stack React/Node.js"
                    maxLength={200}
                  />
                  {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Niveau d'expérience
                    </label>
                    <select
                      value={formData.experience_level}
                      onChange={(e) => updateFormField('experience_level', e.target.value as any)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      {experienceLevels.map((level) => (
                        <option key={level.value} value={level.value}>
                          {level.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Type de contrat
                    </label>
                    <select
                      value={formData.contract_type}
                      onChange={(e) => updateFormField('contract_type', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      {contractTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Localisation *
                    </label>
                    <select
                      value={formData.location}
                      onChange={(e) => updateFormField('location', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                        errors.location ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                      }`}
                    >
                      <option value="">Sélectionner une ville</option>
                      {locations.map((location) => (
                        <option key={location} value={location}>
                          {location}
                        </option>
                      ))}
                    </select>
                    {errors.location && <p className="text-red-500 text-sm mt-1">{errors.location}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Date limite {formData.status === "active" && "*"}
                    </label>
                    <input
                      type="date"
                      value={formData.deadline}
                      onChange={(e) => updateFormField('deadline', e.target.value)}
                      min={new Date().toISOString().split('T')[0]} // Pas de dates passées
                      className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                        errors.deadline ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                      }`}
                    />
                    {errors.deadline && <p className="text-red-500 text-sm mt-1">{errors.deadline}</p>}
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="remote_allowed"
                    checked={formData.remote_allowed}
                    onChange={(e) => updateFormField('remote_allowed', e.target.checked)}
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                  />
                  <label htmlFor="remote_allowed" className="ml-2 block text-sm text-gray-900 dark:text-gray-300">
                    Télétravail autorisé
                  </label>
                </div>
              </CardContent>
            </Card>

            {/* Rémunération */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center text-gray-900 dark:text-white">
                  <DollarSign className="w-5 h-5 mr-2" />
                  Rémunération {formData.status === "active" && "*"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Salaire minimum (MAD) {formData.status === "active" && "*"}
                    </label>
                    <input
                      type="number"
                      value={formData.salary_min}
                      onChange={(e) => updateFormField('salary_min', e.target.value)}
                      min="0"
                      step="100"
                      className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                        errors.salary_min ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                      }`}
                      placeholder="15000"
                    />
                    {errors.salary_min && <p className="text-red-500 text-sm mt-1">{errors.salary_min}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Salaire maximum (MAD) {formData.status === "active" && "*"}
                    </label>
                    <input
                      type="number"
                      value={formData.salary_max}
                      onChange={(e) => updateFormField('salary_max', e.target.value)}
                      min="0"
                      step="100"
                      className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                        errors.salary_max ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                      }`}
                      placeholder="25000"
                    />
                    {errors.salary_max && <p className="text-red-500 text-sm mt-1">{errors.salary_max}</p>}
                  </div>
                </div>
                
                {formData.salary_min && formData.salary_max && (
                  <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    Fourchette: {Number.parseInt(formData.salary_min).toLocaleString()} - {Number.parseInt(formData.salary_max).toLocaleString()} MAD
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Description */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Description du poste *</CardTitle>
              </CardHeader>
              <CardContent>
                <textarea
                  value={formData.description}
                  onChange={(e) => updateFormField('description', e.target.value)}
                  rows={8}
                  maxLength={5000}
                  className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                    errors.description ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                  }`}
                  placeholder="Décrivez le poste, les missions, l'environnement de travail..."
                />
                <div className="flex justify-between items-center mt-1">
                  {errors.description && <p className="text-red-500 text-sm">{errors.description}</p>}
                  <p className="text-gray-500 text-sm ml-auto">{formData.description.length}/5000</p>
                </div>
              </CardContent>
            </Card>

            {/* Exigences */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Exigences et compétences</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newRequirement}
                      onChange={(e) => setNewRequirement(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault()
                          addRequirement()
                        }
                      }}
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Ajouter une compétence ou exigence"
                      maxLength={100}
                    />
                    <Button 
                      onClick={addRequirement} 
                      type="button"
                      disabled={!newRequirement.trim()}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {formData.requirements.map((req, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-full text-sm"
                      >
                        {req}
                        <button
                          onClick={() => removeRequirement(index)}
                          className="ml-2 hover:text-purple-900 dark:hover:text-purple-100"
                          title="Supprimer cette exigence"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>

                  {formData.requirements.length === 0 && (
                    <p className="text-gray-500 text-sm italic">Aucune exigence ajoutée</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Avantages */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Avantages</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newBenefit}
                      onChange={(e) => setNewBenefit(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault()
                          addBenefit()
                        }
                      }}
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Ajouter un avantage"
                      maxLength={100}
                    />
                    <Button 
                      onClick={addBenefit} 
                      type="button"
                      disabled={!newBenefit.trim()}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {formData.benefits.map((benefit, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full text-sm"
                      >
                        {benefit}
                        <button
                          onClick={() => removeBenefit(index)}
                          className="ml-2 hover:text-green-900 dark:hover:text-green-100"
                          title="Supprimer cet avantage"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>

                  {formData.benefits.length === 0 && (
                    <p className="text-gray-500 text-sm italic">Aucun avantage ajouté</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Statut */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Statut</CardTitle>
              </CardHeader>
              <CardContent>
                <select
                  value={formData.status}
                  onChange={(e) => updateFormField('status', e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  {statusOptions.map((status) => (
                    <option key={status.value} value={status.value}>
                      {status.label}
                    </option>
                  ))}
                </select>
                
                <div className="mt-2">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    formData.status === 'active' ? 'bg-green-100 text-green-800' :
                    formData.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                    formData.status === 'closed' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {statusOptions.find(s => s.value === formData.status)?.label}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Aperçu */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Aperçu</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg space-y-3">
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {formData.title || "Titre du poste"}
                  </h3>
                  
                  <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <div className="flex items-center">
                      <Briefcase className="w-4 h-4 mr-2 flex-shrink-0" />
                      <span>{experienceLevels.find(l => l.value === formData.experience_level)?.label}</span>
                    </div>
                    
                    <div className="flex items-center">
                      <MapPin className="w-4 h-4 mr-2 flex-shrink-0" />
                      <span>
                        {formData.location || "Localisation"}
                        {formData.remote_allowed && " (Télétravail possible)"}
                      </span>
                    </div>
                    
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-2 flex-shrink-0" />
                      <span>{formData.contract_type}</span>
                    </div>
                    
                    {formData.salary_min && formData.salary_max && (
                      <div className="flex items-center">
                        <DollarSign className="w-4 h-4 mr-2 flex-shrink-0" />
                        <span>
                          {Number.parseInt(formData.salary_min).toLocaleString()} - {Number.parseInt(formData.salary_max).toLocaleString()} MAD
                        </span>
                      </div>
                    )}
                    
                    {formData.deadline && (
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-2 flex-shrink-0" />
                        <span>
                          Jusqu'au {new Date(formData.deadline).toLocaleDateString('fr-FR')}
                        </span>
                      </div>
                    )}
                  </div>

                  {formData.requirements.length > 0 && (
                    <div className="pt-2 border-t border-gray-200 dark:border-gray-600">
                      <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Compétences:</p>
                      <div className="flex flex-wrap gap-1">
                        {formData.requirements.slice(0, 3).map((req, index) => (
                          <span key={index} className="text-xs bg-purple-50 dark:bg-purple-900/50 text-purple-600 dark:text-purple-400 px-2 py-0.5 rounded">
                            {req}
                          </span>
                        ))}
                        {formData.requirements.length > 3 && (
                          <span className="text-xs text-gray-500">+{formData.requirements.length - 3} autres</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Conseils */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center text-gray-900 dark:text-white">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  Conseils
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
                <div>
                  <strong className="text-gray-800 dark:text-gray-200">Titre accrocheur :</strong> 
                  <span className="ml-1">Utilisez des mots-clés pertinents pour attirer les bons candidats.</span>
                </div>
                <div>
                  <strong className="text-gray-800 dark:text-gray-200">Description claire :</strong> 
                  <span className="ml-1">Décrivez précisément les missions et l'environnement de travail.</span>
                </div>
                <div>
                  <strong className="text-gray-800 dark:text-gray-200">Compétences spécifiques :</strong> 
                  <span className="ml-1">Listez les compétences techniques et soft skills requises.</span>
                </div>
                <div>
                  <strong className="text-gray-800 dark:text-gray-200">Avantages attractifs :</strong> 
                  <span className="ml-1">Mettez en avant ce qui différencie votre entreprise.</span>
                </div>
                <div>
                  <strong className="text-gray-800 dark:text-gray-200">Salaire compétitif :</strong> 
                  <span className="ml-1">Une fourchette salariale claire améliore les candidatures.</span>
                </div>
              </CardContent>
            </Card>

            {/* Statistiques (si mode édition) */}
            {isEditMode && (
              <Card className="dark:bg-gray-800 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="text-gray-900 dark:text-white">Statistiques</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Candidatures:</span>
                    <span className="font-medium text-gray-900 dark:text-white">-</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Vues:</span>
                    <span className="font-medium text-gray-900 dark:text-white">-</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Créée le:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {new Date().toLocaleDateString('fr-FR')}
                    </span>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Actions flottantes sur mobile */}
        <div className="fixed bottom-6 right-6 lg:hidden">
          <div className="flex flex-col space-y-2">
            <Button 
              onClick={() => handleSubmit("draft")} 
              disabled={saving}
              className="shadow-lg"
              size="sm"
            >
              <Save className="w-4 h-4" />
            </Button>
            
            <Button
              onClick={() => handleSubmit("active")}
              disabled={saving || !canPublish}
              className="bg-green-600 hover:bg-green-700 shadow-lg"
              size="sm"
            >
              <Eye className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EditJobPage