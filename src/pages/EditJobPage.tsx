"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { useToast } from "../contexts/ToastContext"
import Header from "../components/Layout/Header"
import Sidebar from "../components/Layout/Sidebar"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { ArrowLeft, Save, Eye, Plus, X, MapPin, DollarSign, Clock, Briefcase, AlertCircle } from "lucide-react"

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
  status: "draft" | "active" | "paused" | "closed"
}

const EditJobPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
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
  })

  const [errors, setErrors] = useState<Partial<JobFormData>>({})

  useEffect(() => {
    fetchJob()
  }, [id])

  const fetchJob = async () => {
    setLoading(true)
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Mock job data
      const mockJob = {
        id: id || "1",
        title: "Développeur Full Stack React/Node.js",
        department: "Technique",
        location: "Casablanca",
        type: "CDI" as const,
        salary: { min: 15000, max: 25000, currency: "MAD" },
        status: "active" as const,
        description: `Nous recherchons un développeur full stack expérimenté pour rejoindre notre équipe technique dynamique. Vous travaillerez sur des projets innovants utilisant les dernières technologies web.

Missions principales :
• Développement d'applications web avec React.js et Node.js
• Conception et implémentation d'APIs REST
• Collaboration avec l'équipe UX/UI pour l'intégration des maquettes
• Participation aux code reviews et à l'amélioration continue
• Maintenance et optimisation des applications existantes`,
        requirements: ["React.js", "Node.js", "MongoDB", "TypeScript", "3+ ans d'expérience"],
        benefits: ["Télétravail hybride", "Assurance santé", "Formation continue"],
        deadline: "2024-02-15",
      }

      setFormData({
        title: mockJob.title,
        department: mockJob.department,
        location: mockJob.location,
        type: mockJob.type,
        salaryMin: mockJob.salary.min.toString(),
        salaryMax: mockJob.salary.max.toString(),
        currency: mockJob.salary.currency,
        description: mockJob.description,
        requirements: mockJob.requirements,
        benefits: mockJob.benefits,
        deadline: mockJob.deadline,
        status: mockJob.status,
      })
    } catch (error) {
      addToast("Erreur lors du chargement de l'offre", "error")
      navigate("/jobs")
    } finally {
      setLoading(false)
    }
  }

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

  const handleSubmit = async (status?: "draft" | "active") => {
    const updatedFormData = status ? { ...formData, status } : formData

    if ((status === "active" || formData.status === "active") && !validateForm()) {
      addToast("Veuillez corriger les erreurs avant de publier", "error")
      return
    }

    setSaving(true)
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500))

      addToast("Offre mise à jour avec succès !", "success")
      navigate(`/jobs/${id}`)
    } catch (error) {
      addToast("Erreur lors de la mise à jour", "error")
    } finally {
      setSaving(false)
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 ml-64 pt-16">
            <div className="flex items-center justify-center h-96">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600"></div>
            </div>
          </main>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 ml-64 pt-16">
          <div className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center space-x-4">
                <Button variant="outline" onClick={() => navigate(`/jobs/${id}`)} className="flex items-center">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Retour
                </Button>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Modifier l'offre</h1>
                  <p className="text-gray-600 dark:text-gray-400">Mettez à jour les informations de l'offre</p>
                </div>
              </div>
              <div className="flex space-x-3">
                <Button variant="outline" onClick={() => handleSubmit("draft")} disabled={saving}>
                  <Save className="w-4 h-4 mr-2" />
                  Sauvegarder
                </Button>
                <Button
                  onClick={() => handleSubmit("active")}
                  disabled={saving}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  {formData.status === "active" ? "Mettre à jour" : "Publier"}
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
                {/* Status */}
                <Card className="dark:bg-gray-800 dark:border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-gray-900 dark:text-white">Statut</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value as JobFormData["status"] })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="draft">Brouillon</option>
                      <option value="active">Active</option>
                      <option value="paused">En pause</option>
                      <option value="closed">Fermée</option>
                    </select>
                  </CardContent>
                </Card>

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
        </main>
      </div>
    </div>
  )
}

export default EditJobPage
