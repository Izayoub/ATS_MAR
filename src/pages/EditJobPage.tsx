"use client"

import type React from "react"
import { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useJobEdit } from "../hooks/useJobEdit"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { ArrowLeft, Save, Eye, Plus, X, AlertCircle, Loader2, RefreshCw } from "lucide-react"

const EditJobPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [newRequirement, setNewRequirement] = useState("")
  const [newBenefit, setNewBenefit] = useState("")

  const {
    formData,
    errors,
    loading,
    saving,
    originalJob,
    saveJob,
    updateField,
    addToList,
    removeFromList,
    resetForm,
    hasChanges,
    isEditMode,
    canPublish,
  } = useJobEdit({
    id,
    onSuccess: (job) => {
      navigate(`/jobs/${job.id}`)
    },
    onError: (error) => {
      console.error("Error editing job:", error)
    },
  })

  const handleSave = async (status?: "draft" | "active") => {
    await saveJob(status)
  }

  const handleAddRequirement = () => {
    if (newRequirement.trim() && addToList("requirements", newRequirement)) {
      setNewRequirement("")
    }
  }

  const handleAddBenefit = () => {
    if (newBenefit.trim() && addToList("benefits", newBenefit)) {
      setNewBenefit("")
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent, action: () => void) => {
    if (e.key === "Enter") {
      e.preventDefault()
      action()
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Chargement de l'offre...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={() => navigate("/jobs")} className="flex items-center">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Retour
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {isEditMode ? "Modifier l'offre" : "Créer une offre"}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {isEditMode ? `Modification de "${originalJob?.title}"` : "Créez une nouvelle offre d'emploi"}
            </p>
          </div>
        </div>
        <div className="flex space-x-3">
          {isEditMode && originalJob && (
            <Button variant="outline" onClick={() => navigate(`/jobs/${originalJob.id}`)}>
              <Eye className="w-4 h-4 mr-2" />
              Aperçu
            </Button>
          )}
          {hasChanges() && (
            <Button variant="outline" onClick={resetForm} className="text-gray-600 bg-transparent">
              <RefreshCw className="w-4 h-4 mr-2" />
              Annuler
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle>Informations générales</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Titre du poste *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => updateField("title", e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white ${
                    errors.title ? "border-red-500" : "border-gray-300"
                  }`}
                  placeholder="Ex: Développeur Full Stack"
                />
                {errors.title && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.title}
                  </p>
                )}
              </div>

              

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Type de contrat
                  </label>
                  <select
                    value={formData.contract_type}
                    onChange={(e) => updateField("contract_type", e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                  >
                    <option value="CDI">CDI</option>
                    <option value="CDD">CDD</option>
                    <option value="Stage">Stage</option>
                    <option value="Freelance">Freelance</option>
                    <option value="Temps partiel">Temps partiel</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Niveau d'expérience
                  </label>
                  <select
                    value={formData.experience_level}
                    onChange={(e) => updateField("experience_level", e.target.value as any)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                  >
                    <option value="junior">Junior (0-2 ans)</option>
                    <option value="middle">Confirmé (2-5 ans)</option>
                    <option value="senior">Senior (5+ ans)</option>
                  </select>
                </div>
              </div>

              

                
                
              

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Date limite de candidature *
                </label>
                <input
                  type="date"
                  value={formData.deadline}
                  onChange={(e) => updateField("deadline", e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white ${
                    errors.deadline ? "border-red-500" : "border-gray-300"
                  }`}
                />
                {errors.deadline && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.deadline}
                  </p>
                )}
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="remote_allowed"
                  checked={formData.remote_allowed}
                  onChange={(e) => updateField("remote_allowed", e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="remote_allowed" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                  Télétravail autorisé
                </label>
              </div>
            </CardContent>
          </Card>

          {/* Description */}
          <Card>
            <CardHeader>
              <CardTitle>Description du poste</CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description détaillée *
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => updateField("description", e.target.value)}
                  rows={8}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white ${
                    errors.description ? "border-red-500" : "border-gray-300"
                  }`}
                  placeholder="Décrivez le poste, les missions, l'environnement de travail..."
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.description}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Requirements */}
          <Card>
            <CardHeader>
              <CardTitle>Exigences et compétences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newRequirement}
                  onChange={(e) => setNewRequirement(e.target.value)}
                  onKeyPress={(e) => handleKeyPress(e, handleAddRequirement)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                  placeholder="Ajouter une exigence..."
                />
                <Button onClick={handleAddRequirement} size="sm">
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.requirements.map((req, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-sm"
                  >
                    {req}
                    <button
                      onClick={() => removeFromList("requirements", index)}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Benefits */}
          <Card>
            <CardHeader>
              <CardTitle>Avantages</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newBenefit}
                  onChange={(e) => setNewBenefit(e.target.value)}
                  onKeyPress={(e) => handleKeyPress(e, handleAddBenefit)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                  placeholder="Ajouter un avantage..."
                />
                <Button onClick={handleAddBenefit} size="sm">
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
                      onClick={() => removeFromList("benefits", index)}
                      className="ml-2 text-green-600 hover:text-green-800"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status */}
          <Card>
            <CardHeader>
              <CardTitle>Statut de l'offre</CardTitle>
            </CardHeader>
            <CardContent>
              <select
                value={formData.status}
                onChange={(e) => updateField("status", e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              >
                <option value="draft">Brouillon</option>
                <option value="active">Active</option>
                <option value="paused">En pause</option>
                <option value="closed">Fermée</option>
              </select>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {formData.status === "draft" && "L'offre ne sera pas visible publiquement"}
                {formData.status === "active" && "L'offre sera visible et les candidatures acceptées"}
                {formData.status === "paused" && "L'offre est visible mais les candidatures sont suspendues"}
                {formData.status === "closed" && "L'offre est fermée aux nouvelles candidatures"}
              </p>
            </CardContent>
          </Card>

          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                onClick={() => handleSave("draft")}
                disabled={saving}
                className="w-full justify-start"
                variant="outline"
              >
                {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Sauvegarder en brouillon
              </Button>

              <Button
                onClick={() => handleSave("active")}
                disabled={saving || !canPublish}
                className="w-full justify-start"
              >
                {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                {isEditMode ? "Sauvegarder et publier" : "Créer et publier"}
              </Button>

              {!canPublish && (
                <p className="text-sm text-amber-600 dark:text-amber-400 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  Remplissez les champs obligatoires pour publier
                </p>
              )}
            </CardContent>
          </Card>

          {/* Help */}
          <Card>
            <CardHeader>
              <CardTitle>Conseils</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
              <p>• Utilisez un titre clair et descriptif</p>
              <p>• Détaillez les missions et responsabilités</p>
              <p>• Listez les compétences techniques requises</p>
              <p>• Mentionnez les avantages attractifs</p>
              <p>• Fixez une date limite réaliste</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default EditJobPage
