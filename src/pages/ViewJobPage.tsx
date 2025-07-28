"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useParams, useNavigate, Link } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { useToast } from "../contexts/ToastContext"
import Header from "../components/Layout/Header"
import Sidebar from "../components/Layout/Sidebar"
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

interface Job {
  id: string
  title: string
  department: string
  location: string
  type: "CDI" | "CDD" | "Stage" | "Freelance"
  salary: {
    min: number
    max: number
    currency: string
  }
  status: "active" | "paused" | "closed" | "draft"
  applicants: number
  views: number
  createdAt: string
  deadline: string
  description: string
  requirements: string[]
  benefits: string[]
}

const ViewJobPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const [job, setJob] = useState<Job | null>(null)
  const [loading, setLoading] = useState(true)
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  useEffect(() => {
    fetchJob()
  }, [id])

  const fetchJob = async () => {
    setLoading(true)
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Mock job data
      const mockJob: Job = {
        id: id || "1",
        title: "Développeur Full Stack React/Node.js",
        department: "Technique",
        location: "Casablanca",
        type: "CDI",
        salary: { min: 15000, max: 25000, currency: "MAD" },
        status: "active",
        applicants: 24,
        views: 156,
        createdAt: "2024-01-15",
        deadline: "2024-02-15",
        description: `Nous recherchons un développeur full stack expérimenté pour rejoindre notre équipe technique dynamique. Vous travaillerez sur des projets innovants utilisant les dernières technologies web.

Missions principales :
• Développement d'applications web avec React.js et Node.js
• Conception et implémentation d'APIs REST
• Collaboration avec l'équipe UX/UI pour l'intégration des maquettes
• Participation aux code reviews et à l'amélioration continue
• Maintenance et optimisation des applications existantes

Environnement technique :
• Frontend : React.js, TypeScript, Tailwind CSS
• Backend : Node.js, Express.js, MongoDB
• Outils : Git, Docker, AWS
• Méthodologie : Agile/Scrum`,
        requirements: ["React.js", "Node.js", "MongoDB", "TypeScript", "3+ ans d'expérience", "Git", "API REST"],
        benefits: [
          "Télétravail hybride",
          "Assurance santé",
          "Formation continue",
          "Tickets restaurant",
          "Équipe jeune et dynamique",
        ],
      }

      setJob(mockJob)
    } catch (error) {
      addToast("Erreur lors du chargement de l'offre", "error")
      navigate("/jobs")
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (newStatus: Job["status"]) => {
    if (!job) return

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500))

      setJob({ ...job, status: newStatus })
      addToast(
        newStatus === "active" ? "Offre activée" : newStatus === "paused" ? "Offre mise en pause" : "Offre fermée",
        "success",
      )
    } catch (error) {
      addToast("Erreur lors de la mise à jour", "error")
    }
  }

  const handleDelete = async () => {
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500))

      addToast("Offre supprimée avec succès", "success")
      navigate("/jobs")
    } catch (error) {
      addToast("Erreur lors de la suppression", "error")
    }
  }

  const copyJobLink = () => {
    const link = `${window.location.origin}/jobs/${job?.id}/public`
    navigator.clipboard.writeText(link)
    addToast("Lien copié dans le presse-papiers", "success")
  }

  const getStatusColor = (status: Job["status"]) => {
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

  const getStatusText = (status: Job["status"]) => {
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

  if (!job) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 ml-64 pt-16">
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Offre introuvable</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">Cette offre n'existe pas ou a été supprimée.</p>
                <Button onClick={() => navigate("/jobs")}>Retour aux offres</Button>
              </div>
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
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">
                    Créée le {new Date(job.createdAt).toLocaleDateString("fr-FR")}
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
                          <div className="text-sm text-gray-600 dark:text-gray-400">Département</div>
                          <div className="font-medium text-gray-900 dark:text-white">{job.department}</div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                          <MapPin className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">Localisation</div>
                          <div className="font-medium text-gray-900 dark:text-white">{job.location}</div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                          <Clock className="w-5 h-5 text-green-600 dark:text-green-400" />
                        </div>
                        <div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">Type</div>
                          <div className="font-medium text-gray-900 dark:text-white">{job.type}</div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
                          <DollarSign className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                        </div>
                        <div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">Salaire</div>
                          <div className="font-medium text-gray-900 dark:text-white">
                            {job.salary.min.toLocaleString()} - {job.salary.max.toLocaleString()} {job.salary.currency}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Description du poste</h3>
                        <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                          <Calendar className="w-4 h-4 mr-1" />
                          Échéance : {new Date(job.deadline).toLocaleDateString("fr-FR")}
                        </div>
                      </div>
                      <div className="prose dark:prose-invert max-w-none">
                        <div className="whitespace-pre-line text-gray-700 dark:text-gray-300">{job.description}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Requirements */}
                <Card className="dark:bg-gray-800 dark:border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-gray-900 dark:text-white">Exigences et compétences</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {job.requirements.map((req, index) => (
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

                {/* Benefits */}
                <Card className="dark:bg-gray-800 dark:border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-gray-900 dark:text-white">Avantages</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {job.benefits.map((benefit, index) => (
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
                      <span className="text-2xl font-bold text-gray-900 dark:text-white">{job.applicants}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">Vues</span>
                      </div>
                      <span className="text-2xl font-bold text-gray-900 dark:text-white">{job.views}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">Taux de conversion</span>
                      </div>
                      <span className="text-2xl font-bold text-gray-900 dark:text-white">
                        {Math.round((job.applicants / job.views) * 100)}%
                      </span>
                    </div>
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
                        Voir les candidats ({job.applicants})
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

                {/* Deadline Alert */}
                {new Date(job.deadline) < new Date() && job.status === "active" && (
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
        </main>
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
