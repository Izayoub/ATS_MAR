"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useParams, useNavigate, Link } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { useToast } from "../contexts/ToastContext"
import jobService from "../services/JobService"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import {
  ArrowLeft,
  Edit,
  Trash2,
  Users,
  Eye,
  Share2,
  Play,
  Pause,
  MapPin,
  DollarSign,
  Clock,
  Briefcase,
  Calendar,
  TrendingUp,
  AlertCircle,
  ExternalLink,
  Copy,
} from "lucide-react"

// Interface basée sur votre modèle Django
interface JobOffer {
  id: number
  title: string
  description: string
  requirements: string
  benefits: string
  status: 'draft' | 'active' | 'paused' | 'closed'
  experience_level: 'junior' | 'middle' | 'senior'
  salary_min: number | null
  salary_max: number | null
  location: string
  remote_allowed: boolean
  contract_type: string
  company: {
    id: number
    name: string
  }
  created_by: {
    id: number
    username: string
    email: string
  }
  created_at: string
  updated_at: string
  deadline: string | null
  ai_generated: boolean
  seo_optimized: boolean
  bias_checked: boolean
  applications_count?: number
  views_count?: number
}

const ViewJobPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const [job, setJob] = useState<JobOffer | null>(null)
  const [loading, setLoading] = useState(true)
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  useEffect(() => {
    if (id) {
      fetchJob()
    }
  }, [id])

  const fetchJob = async () => {
    if (!id) return
    
    setLoading(true)
    try {
      const response = await jobService.getJob(parseInt(id))
      setJob(response)
    } catch (error: any) {
      addToast("Erreur lors du chargement de l'offre", "error")
      navigate("/jobs")
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (newStatus: JobOffer["status"]) => {
    if (!job) return

    try {
      const updatedJob = await jobService.updateJob(job.id, { status: newStatus })
      setJob(updatedJob)
      
      const statusMessages = {
        active: "Offre activée",
        paused: "Offre mise en pause", 
        closed: "Offre fermée",
        draft: "Offre remise en brouillon"
      }
      
      addToast(statusMessages[newStatus], "success")
    } catch (error: any) {
      addToast("Erreur lors de la mise à jour", "error")
    }
  }

  const handleDelete = async () => {
    if (!job) return

    try {
      await jobService.deleteJob(job.id)
      addToast("Offre supprimée avec succès", "success")
      navigate("/jobs")
    } catch (error: any) {
      addToast("Erreur lors de la suppression", "error")
    }
  }

  const copyJobLink = () => {
    const link = `${window.location.origin}/jobs/${job?.id}/public`
    navigator.clipboard.writeText(link)
    addToast("Lien copié dans le presse-papiers", "success")
  }

  const getStatusColor = (status: JobOffer["status"]) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      case "paused":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
      case "closed":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
      case "draft":
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getStatusText = (status: JobOffer["status"]) => {
    switch (status) {
      case "active":
        return "Active"
      case "paused":
        return "En pause"
      case "closed":
        return "Fermée"
      case "draft":
        return "Brouillon"
      default:
        return status
    }
  }

  const getExperienceLevelText = (level: string) => {
    switch (level) {
      case 'junior':
        return 'Junior (0-2 ans)'
      case 'middle':
        return 'Confirmé (2-5 ans)'
      case 'senior':
        return 'Senior (5+ ans)'
      default:
        return level
    }
  }

  const formatSalary = (min: number | null, max: number | null) => {
    if (!min && !max) return "Non spécifié"
    if (min && max) return `${min.toLocaleString()} - ${max.toLocaleString()} MAD`
    if (min) return `À partir de ${min.toLocaleString()} MAD`
    if (max) return `Jusqu'à ${max.toLocaleString()} MAD`
    return "Non spécifié"
  }

  const parseListField = (field: string): string[] => {
    if (!field) return []
    
    // Nettoie le texte et divise par différents séparateurs possibles
    return field
      .split(/\n|•|\*|-|\||,|;/)
      .map(item => item.trim())
      .filter(item => item.length > 0 && !item.match(/^\s*$/))
      .slice(0, 20) // Limite à 20 éléments pour éviter l'encombrement
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Offre introuvable</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">Cette offre n'existe pas ou a été supprimée.</p>
            <Button onClick={() => navigate("/jobs")}>Retour aux offres</Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={() => navigate("/jobs")} className="flex items-center">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Retour
            </Button>
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{job.title}</h1>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(job.status)}`}>
                  {getStatusText(job.status)}
                </span>
                {job.ai_generated && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded-full text-xs font-medium">
                    IA
                  </span>
                )}
              </div>
              <p className="text-gray-600 dark:text-gray-400">
                Créée le {new Date(job.created_at).toLocaleDateString("fr-FR")}
              </p>
            </div>
          </div>
          <div className="flex space-x-3">
            <Button variant="outline" onClick={copyJobLink}>
              <Share2 className="w-4 h-4 mr-2" />
              Partager
            </Button>
            <Button variant="outline" onClick={() => navigate(`/jobs/${job.id}/edit`)}>
              <Edit className="w-4 h-4 mr-2" />
              Modifier
            </Button>
            <Button variant="outline" onClick={() => setShowDeleteModal(true)} className="text-red-600">
              <Trash2 className="w-4 h-4 mr-2" />
              Supprimer
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Job Details */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardContent className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                      <Briefcase className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">Entreprise</div>
                      <div className="font-medium text-gray-900 dark:text-white">{job.company.name}</div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                      <MapPin className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">Localisation</div>
                      <div className="font-medium text-gray-900 dark:text-white">
                        {job.location}
                        {job.remote_allowed && (
                          <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                            Télétravail
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                      <Clock className="w-5 h-5 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">Type / Expérience</div>
                      <div className="font-medium text-gray-900 dark:text-white">
                        {job.contract_type}
                        <br />
                        <span className="text-xs text-gray-500">
                          {getExperienceLevelText(job.experience_level)}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
                      <DollarSign className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">Salaire</div>
                      <div className="font-medium text-gray-900 dark:text-white text-sm">
                        {formatSalary(job.salary_min, job.salary_max)}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Description du poste</h3>
                    {job.deadline && (
                      <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                        <Calendar className="w-4 h-4 mr-1" />
                        Échéance : {new Date(job.deadline).toLocaleDateString("fr-FR")}
                      </div>
                    )}
                  </div>
                  <div className="prose dark:prose-invert max-w-none">
                    <div className="whitespace-pre-line text-gray-700 dark:text-gray-300">{job.description}</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Requirements */}
            {job.requirements && (
              <Card className="dark:bg-gray-800 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="text-gray-900 dark:text-white">Exigences et compétences</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex  flex-wrap gap-2">
                    {parseListField(job.requirements).map((req, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-full text-sm"
                      >
                        {req}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Benefits */}
            {job.benefits && (
              <Card className="dark:bg-gray-800 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="text-gray-900 dark:text-white">Avantages</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {parseListField(job.benefits).map((benefit, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full text-sm"
                      >
                        {benefit}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Stats */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Statistiques</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Users className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">Candidatures</span>
                  </div>
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">
                    {job.applications_count || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">Vues</span>
                  </div>
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">
                    {job.views_count || 0}
                  </span>
                </div>
                {job.applications_count && job.views_count && job.views_count > 0 && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">Taux de conversion</span>
                    </div>
                    <span className="text-2xl font-bold text-gray-900 dark:text-white">
                      {Math.round((job.applications_count / job.views_count) * 100)}%
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Actions */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Link to={`/candidates?job=${job.id}`} className="block">
                  <Button className="w-full justify-start">
                    <Users className="w-4 h-4 mr-2" />
                    Voir les candidats ({job.applications_count || 0})
                  </Button>
                </Link>

                {job.status === "active" ? (
                  <Button
                    variant="outline"
                    className="w-full justify-start bg-transparent"
                    onClick={() => handleStatusChange("paused")}
                  >
                    <Pause className="w-4 h-4 mr-2" />
                    Mettre en pause
                  </Button>
                ) : job.status === "paused" ? (
                  <Button
                    variant="outline"
                    className="w-full justify-start bg-transparent"
                    onClick={() => handleStatusChange("active")}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Réactiver
                  </Button>
                ) : job.status === "draft" ? (
                  <Button
                    variant="outline"
                    className="w-full justify-start bg-transparent"
                    onClick={() => handleStatusChange("active")}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Publier
                  </Button>
                ) : null}

                <Button variant="outline" className="w-full justify-start bg-transparent" onClick={copyJobLink}>
                  <Copy className="w-4 h-4 mr-2" />
                  Copier le lien
                </Button>

                <Button
                  variant="outline"
                  className="w-full justify-start bg-transparent"
                  onClick={() => window.open(`/jobs/${job.id}/public`, "_blank")}
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Vue publique
                </Button>
              </CardContent>
            </Card>

            {/* Quality Indicators */}
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Qualité de l'offre</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Optimisé SEO</span>
                  <span className={`text-xs px-2 py-1 rounded ${job.seo_optimized ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                    {job.seo_optimized ? 'Oui' : 'Non'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Vérifié anti-biais</span>
                  <span className={`text-xs px-2 py-1 rounded ${job.bias_checked ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                    {job.bias_checked ? 'Oui' : 'Non'}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Deadline Alert */}
            {job.deadline && new Date(job.deadline) < new Date() && job.status === "active" && (
              <Card className="border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
                    <AlertCircle className="w-5 h-5" />
                    <div>
                      <div className="font-medium">Échéance dépassée</div>
                      <div className="text-sm">Cette offre a dépassé sa date limite de candidature.</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>

      {/* Delete Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center">
                <Trash2 className="w-5 h-5 text-red-600 dark:text-red-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Supprimer l'offre</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Cette action est irréversible</p>
              </div>
            </div>
            <p className="text-gray-700 dark:text-gray-300 mb-6">
              Êtes-vous sûr de vouloir supprimer l'offre "{job.title}" ? Toutes les candidatures associées seront
              également supprimées.
            </p>
            <div className="flex space-x-3">
              <Button variant="outline" onClick={() => setShowDeleteModal(false)} className="flex-1">
                Annuler
              </Button>
              <Button onClick={handleDelete} className="flex-1 bg-red-600 hover:bg-red-700">
                Supprimer
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ViewJobPage