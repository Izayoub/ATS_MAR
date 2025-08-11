"use client"

import type React from "react"
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { useToast } from "../contexts/ToastContext"
import Header from "../components/Layout/Header"
import Sidebar from "../components/Layout/Sidebar"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { ArrowLeft, Save, Eye, Plus, X, MapPin, DollarSign, Clock, Briefcase, AlertCircle } from "lucide-react"
import jobService from "../services/JobService"

interface JobFormData {
  title: string
  department: string
  location: string
  type: "CDI" | "CDD" | "Stage" | "Freelance"
  salaryMin: string
  salaryMax: string
  currency: string
  description: string
  requirements: string[]
  benefits: string[]
  deadline: string
  status: "draft" | "active"
  experience_level: "junior" | "middle" | "senior"
  remote_allowed: boolean
  contract_type: string
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
    location: "",
    type: "CDI",
    salaryMin: "",
    salaryMax: "",
    currency: "MAD",
    description: "",
    requirements: [],
    benefits: [],
    deadline: "",
    status: "draft",
    experience_level: "junior",
    remote_allowed: false,
    contract_type: "CDI",
  })

  const [errors, setErrors] = useState<Partial<JobFormData>>({})

  const validateForm = (): boolean => {
    const newErrors: Partial<JobFormData> = {}

    if (!formData.title.trim()) newErrors.title = "Le titre est requis"
    if (!formData.department.trim()) newErrors.department = "Le département est requis"
    if (!formData.location.trim()) newErrors.location = "La localisation est requise"
    if (!formData.description.trim()) newErrors.description = "La description est requise"
    if (!formData.deadline) newErrors.deadline = "La date limite est requise"
    if (!formData.salaryMin) newErrors.salaryMin = "Le salaire minimum est requis"
    if (!formData.salaryMax) newErrors.salaryMax = "Le salaire maximum est requis"

    if (formData.salaryMin && formData.salaryMax) {
      if (Number.parseInt(formData.salaryMin) >= Number.parseInt(formData.salaryMax)) {
        newErrors.salaryMax = "Le salaire maximum doit être supérieur au minimum"
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (status: "draft" | "active") => {
    const updatedFormData = { ...formData, status }
    setFormData(updatedFormData)

    if (status === "active" && !validateForm()) {
      addToast("Veuillez corriger les erreurs avant de publier", "error")
      return
    }

    setLoading(true)
    try {
      // Prepare payload for backend
      const payload = {
        title: updatedFormData.title,
        description: updatedFormData.description,
        requirements: updatedFormData.requirements.join("\n"),
        benefits: updatedFormData.benefits.join("\n"),
        status: updatedFormData.status,
        experience_level: updatedFormData.experience_level,
        salary_min: updatedFormData.salaryMin ? Number(updatedFormData.salaryMin) : null,
        salary_max: updatedFormData.salaryMax ? Number(updatedFormData.salaryMax) : null,
        location: updatedFormData.location,
        remote_allowed: updatedFormData.remote_allowed,
        contract_type: updatedFormData.type,
        deadline: updatedFormData.deadline ? updatedFormData.deadline : null,
        // department is not in backend model, so not sent
      }
      await jobService.createJob(payload)
      addToast(status === "active" ? "Offre publiée avec succès !" : "Brouillon sauvegardé !", "success")
      navigate("/jobs")
    } catch (error) {
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

  const departments = ["Technique", "Marketing", "Ventes", "RH", "Finance", "Design", "Data", "Support", "Direction"]

  const locations = [
    "Casablanca",
    "Rabat",
    "Marrakech",
    "Fès",
    "Tanger",
    "Agadir",
    "Meknès",
    "Oujda",
    "Télétravail",
    "Hybride",
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      
      <div className="flex">
        
        
          <div className="p-6">
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
                  className="bg-green-600 hover:bg-green-700"
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
                          Localisation *
                        </label>
                        <select
                          value={formData.location}
                          onChange={(e) => setFormData({ ...formData, location: e.target.value })}
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
                          className="mr-2"
                          id="remote_allowed"
                        />
                        <label htmlFor="remote_allowed" className="text-sm text-gray-700 dark:text-gray-300">
                          Télétravail autorisé
                        </label>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Salary */}
                <Card className="dark:bg-gray-800 dark:border-gray-700">
                  <CardHeader>
                    <CardTitle className="flex items-center text-gray-900 dark:text-white">
                      <DollarSign className="w-5 h-5 mr-2" />
                      Rémunération
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Salaire minimum *
                        </label>
                        <input
                          type="number"
                          value={formData.salaryMin}
                          onChange={(e) => setFormData({ ...formData, salaryMin: e.target.value })}
                          className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                            errors.salaryMin ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                          }`}
                          placeholder="15000"
                        />
                        {errors.salaryMin && <p className="text-red-500 text-sm mt-1">{errors.salaryMin}</p>}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Salaire maximum *
                        </label>
                        <input
                          type="number"
                          value={formData.salaryMax}
                          onChange={(e) => setFormData({ ...formData, salaryMax: e.target.value })}
                          className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                            errors.salaryMax ? "border-red-500" : "border-gray-300 dark:border-gray-600"
                          }`}
                          placeholder="25000"
                        />
                        {errors.salaryMax && <p className="text-red-500 text-sm mt-1">{errors.salaryMax}</p>}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Devise
                        </label>
                        <select
                          value={formData.currency}
                          onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        >
                          <option value="MAD">MAD</option>
                          <option value="EUR">EUR</option>
                          <option value="USD">USD</option>
                        </select>
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
                          <MapPin className="w-4 h-4 mr-2" />
                          {formData.location || "Localisation"}
                        </div>
                        <div className="flex items-center">
                          <Clock className="w-4 h-4 mr-2" />
                          {formData.type}
                        </div>
                        {formData.salaryMin && formData.salaryMax && (
                          <div className="flex items-center">
                            <DollarSign className="w-4 h-4 mr-2" />
                            {Number.parseInt(formData.salaryMin).toLocaleString()} -{" "}
                            {Number.parseInt(formData.salaryMax).toLocaleString()} {formData.currency}
                          </div>
                        )}
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
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        
      </div>
    </div>
  )
}

export default CreateJobPage
