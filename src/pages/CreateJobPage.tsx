"use client"

import type React from "react"
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { useToast } from "../contexts/ToastContext"
import Layout from "../components/Layout/Layout"
import MatchingConfigComponent from "../components/Matching/MatchingConfigComponent"

import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { ArrowLeft, Save, Eye, Plus, X, Clock, Briefcase, AlertCircle } from "lucide-react"
import jobService from "../services/JobService"
import type { MatchingWeights, DEFAULT_MATCHING_WEIGHTS } from "../types/api"

interface JobFormData {
  title: string
  department: string
  type: "CDI" | "CDD" | "Stage" | "Freelance"
  currency: string
  description: string
  requirements: string[]
  benefits: string[]
  deadline: string
  status: "draft" | "active"
  experience_level: "junior" | "middle" | "senior"
  remote_allowed: boolean
  contract_type: string
  matching_weights?: MatchingWeights
  system_prompt?: string
}

const CreateJobPage: React.FC = () => {
  const { user } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [newRequirement, setNewRequirement] = useState("")
  const [newBenefit, setNewBenefit] = useState("")

  const [formData, setFormData] = useState<JobFormData>({
    title: "",
    department: "",
    type: "CDI",
    currency: "MAD",
    description: "",
    requirements: [],
    benefits: [],
    deadline: "",
    status: "draft",
    experience_level: "junior",
    remote_allowed: false,
    contract_type: "CDI",
    matching_weights: undefined,
    system_prompt: undefined,
  })

  const [errors, setErrors] = useState<Partial<JobFormData>>({})

  const validateForm = (): boolean => {
    const newErrors: Partial<JobFormData> = {}

    if (!formData.title.trim()) newErrors.title = "Le titre est requis"
    if (!formData.department.trim()) newErrors.department = "Le département est requis"
    if (!formData.description.trim()) newErrors.description = "La description est requise"
    if (!formData.deadline) newErrors.deadline = "La date limite est requise"

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (status: "draft" | "active") => {
    if (status === "active" && !validateForm()) {
      addToast("Veuillez corriger les erreurs avant de publier", "error")
      return
    }

    setLoading(true)
    try {
      const payload = {
        title: formData.title,
        description: formData.description,
        requirements: formData.requirements.join("\n"),
        benefits: formData.benefits.join("\n"),
        status: status,
        experience_level: formData.experience_level,
        remote_allowed: formData.remote_allowed,
        contract_type: formData.type,
        deadline: formData.deadline ? formData.deadline : null,
        ...(formData.matching_weights && { matching_weights: formData.matching_weights }),
        system_prompt: formData.system_prompt?.trim() || "",
      }
      
      const createdJob = await jobService.createJob(payload)
      addToast(status === "active" ? "Offre publiée avec succès !" : "Brouillon sauvegardé !", "success")
      navigate(`/jobs/${createdJob.id}`)
    } catch (error) {
      console.error('Error creating job:', error)
      addToast("Erreur lors de la sauvegarde", "error")
    } finally {
      setLoading(false)
    }
  }

  const addRequirement = () => {
    if (newRequirement.trim() && !formData.requirements.includes(newRequirement.trim())) {
      setFormData({
        ...formData,
        requirements: [...formData.requirements, newRequirement.trim()],
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
    if (newBenefit.trim() && !formData.benefits.includes(newBenefit.trim())) {
      setFormData({
        ...formData,
        benefits: [...formData.benefits, newBenefit.trim()],
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

  const handleMatchingConfigUpdate = (config: { 
    matching_weights?: MatchingWeights
    system_prompt?: string 
  }) => {
    setFormData(prev => ({
      ...prev,
      matching_weights: config.matching_weights,
      system_prompt: config.system_prompt,
    }))
  }

  const departments = ["Technique", "Marketing", "Ventes", "RH", "Finance", "Design", "Data", "Support", "Direction"]

  return (
    <Layout>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={() => navigate("/jobs")} className="flex items-center">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Retour
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Créer une offre</h1>
            <p className="text-gray-600 dark:text-gray-400">Publiez une nouvelle offre d'emploi</p>
          </div>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" onClick={() => handleSubmit("draft")} disabled={loading}>
            <Save className="w-4 h-4 mr-2" />
            Sauvegarder brouillon
          </Button>
          <Button
            onClick={() => handleSubmit("active")}
            disabled={loading}
            className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
          >
            <Eye className="w-4 h-4 mr-2" />
            Publier l'offre
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
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
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                    errors.title ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                  }`}
                  placeholder="Ex: Développeur Full Stack React/Node.js"
                />
                {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Département *
                  </label>
                  <select
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                      errors.department ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                    }`}
                  >
                    <option value="">Sélectionner un département</option>
                    {departments.map((dept) => (
                      <option key={dept} value={dept}>
                        {dept}
                      </option>
                    ))}
                  </select>
                  {errors.department && <p className="text-red-500 text-sm mt-1">{errors.department}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Type de contrat
                  </label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value as JobFormData["type"] })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="CDI">CDI</option>
                    <option value="CDD">CDD</option>
                    <option value="Stage">Stage</option>
                    <option value="Freelance">Freelance</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Date limite *
                  </label>
                  <input
                    type="date"
                    value={formData.deadline}
                    onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                    className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                      errors.deadline ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                    }`}
                  />
                  {errors.deadline && <p className="text-red-500 text-sm mt-1">{errors.deadline}</p>}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Niveau d'expérience
                  </label>
                  <select
                    value={formData.experience_level}
                    onChange={(e) => setFormData({ ...formData, experience_level: e.target.value as JobFormData["experience_level"] })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="junior">Junior (0-2 ans)</option>
                    <option value="middle">Confirmé (2-5 ans)</option>
                    <option value="senior">Senior (5+ ans)</option>
                  </select>
                </div>
                <div className="flex items-center mt-6">
                  <input
                    type="checkbox"
                    checked={formData.remote_allowed}
                    onChange={(e) => setFormData({ ...formData, remote_allowed: e.target.checked })}
                    className="mr-2 w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                    id="remote_allowed"
                  />
                  <label htmlFor="remote_allowed" className="text-sm text-gray-700 dark:text-gray-300">
                    Télétravail autorisé
                  </label>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Description */}
          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardHeader>
              <CardTitle className="text-gray-900 dark:text-white">Description du poste</CardTitle>
            </CardHeader>
            <CardContent>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={8}
                className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                  errors.description ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                }`}
                placeholder="Décrivez le poste, les missions, l'environnement de travail..."
              />
              {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
            </CardContent>
          </Card>

          {/* Requirements */}
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
                    onKeyPress={(e) => e.key === "Enter" && addRequirement()}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Ajouter une compétence ou exigence"
                  />
                  <Button onClick={addRequirement} type="button">
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
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Benefits */}
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
                    onKeyPress={(e) => e.key === "Enter" && addBenefit()}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Ajouter un avantage"
                  />
                  <Button onClick={addBenefit} type="button">
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
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Configuration de matching personnalisé */}
          <MatchingConfigComponent
            jobId={0}
            currentWeights={formData.matching_weights}
            currentPrompt={formData.system_prompt}
            isCustomized={!!(formData.matching_weights || formData.system_prompt)}
            mode="creation"
            onConfigChange={handleMatchingConfigUpdate}
            className="mb-6"
          />
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Preview */}
          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardHeader>
              <CardTitle className="text-gray-900 dark:text-white">Aperçu</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  {formData.title || "Titre du poste"}
                </h3>
                <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center">
                    <Briefcase className="w-4 h-4 mr-2" />
                    {formData.department || "Département"}
                  </div>
                  
                  <div className="flex items-center">
                    <Clock className="w-4 h-4 mr-2" />
                    {formData.type}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tips */}
          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardHeader>
              <CardTitle className="flex items-center text-gray-900 dark:text-white">
                <AlertCircle className="w-5 h-5 mr-2" />
                Conseils
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
              <div>
                <strong>Titre accrocheur :</strong> Utilisez des mots-clés pertinents pour attirer les bons
                candidats.
              </div>
              <div>
                <strong>Description claire :</strong> Décrivez précisément les missions et l'environnement de
                travail.
              </div>
              <div>
                <strong>Compétences spécifiques :</strong> Listez les compétences techniques et soft skills
                requises.
              </div>
              <div>
                <strong>Avantages attractifs :</strong> Mettez en avant ce qui différencie votre entreprise.
              </div>
              <div>
                <strong>Matching IA :</strong> Personnalisez les critères de matching pour des résultats plus précis.
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  )
}

export default CreateJobPage
