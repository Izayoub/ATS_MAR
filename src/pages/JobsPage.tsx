"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import { useToast } from "../contexts/ToastContext"
import { useNavigate } from "react-router-dom"
import Header from "../components/Layout/Header"
import Sidebar from "../components/Layout/Sidebar"
import { Button } from "../components/ui/button"
import { Card, CardContent } from "../components/ui/card"
import {
  Plus,
  Search,
  Filter,
  MoreVertical,
  Eye,
  Edit,
  Users,
  MapPin,
  DollarSign,
  Briefcase,
  Clock,
  TrendingUp,
  AlertCircle,
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

const JobsPage: React.FC = () => {
  const { user } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    fetchJobs()
  }, [])

  const fetchJobs = async () => {
    setLoading(true)
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      const mockJobs: Job[] = [
        {
          id: "1",
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
          description: "Nous recherchons un développeur full stack expérimenté...",
          requirements: ["React.js", "Node.js", "MongoDB", "3+ ans d'expérience"],
          benefits: ["Télétravail hybride", "Assurance santé", "Formation continue"],
        },
        {
          id: "2",
          title: "Chef de Projet Digital",
          department: "Marketing",
          location: "Rabat",
          type: "CDI",
          salary: { min: 18000, max: 28000, currency: "MAD" },
          status: "active",
          applicants: 18,
          views: 89,
          createdAt: "2024-01-10",
          deadline: "2024-02-10",
          description: "Pilotage de projets digitaux innovants...",
          requirements: ["Gestion de projet", "Marketing digital", "5+ ans d'expérience"],
          benefits: ["Voiture de fonction", "Bonus performance", "Congés flexibles"],
        },
        {
          id: "3",
          title: "Data Scientist",
          department: "Data",
          location: "Casablanca",
          type: "CDI",
          salary: { min: 20000, max: 35000, currency: "MAD" },
          status: "paused",
          applicants: 31,
          views: 203,
          createdAt: "2024-01-05",
          deadline: "2024-02-05",
          description: "Analyse de données et machine learning...",
          requirements: ["Python", "Machine Learning", "SQL", "PhD ou Master"],
          benefits: ["Stock options", "Formation IA", "Conférences internationales"],
        },
        {
          id: "4",
          title: "Stagiaire Marketing Digital",
          department: "Marketing",
          location: "Casablanca",
          type: "Stage",
          salary: { min: 3000, max: 4000, currency: "MAD" },
          status: "active",
          applicants: 67,
          views: 234,
          createdAt: "2024-01-20",
          deadline: "2024-03-01",
          description: "Stage de 6 mois en marketing digital...",
          requirements: ["Étudiant Bac+3/4", "Réseaux sociaux", "Google Analytics"],
          benefits: ["Encadrement expert", "Certification Google", "Possibilité CDI"],
        },
      ]

      setJobs(mockJobs)
    } catch (error) {
      addToast("Erreur lors du chargement des offres", "error")
    } finally {
      setLoading(false)
    }
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

  const filteredJobs = jobs.filter((job) => {
    const matchesSearch =
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.department.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || job.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const stats = [
    {
      title: "Total Offres",
      value: jobs.length.toString(),
      change: "+3",
      changeLabel: "ce mois",
      icon: Briefcase,
      color: "bg-blue-500",
    },
    {
      title: "Offres Actives",
      value: jobs.filter((j) => j.status === "active").length.toString(),
      change: "+2",
      changeLabel: "cette semaine",
      icon: TrendingUp,
      color: "bg-green-500",
    },
    {
      title: "Total Candidatures",
      value: jobs.reduce((sum, job) => sum + job.applicants, 0).toString(),
      change: "+45",
      changeLabel: "cette semaine",
      icon: Users,
      color: "bg-purple-500",
    },
    {
      title: "Taux de Vue",
      value: "87%",
      change: "+5%",
      changeLabel: "vs mois dernier",
      icon: Eye,
      color: "bg-orange-500",
    },
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
            <div className="flex justify-between items-center mb-8">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Offres d'emploi</h1>
                <p className="text-gray-600 dark:text-gray-400">Gérez vos offres et suivez les candidatures</p>
              </div>
              <Button onClick={() => navigate("/jobs/create")} size="lg">
                <Plus className="w-4 h-4 mr-2" />
                Nouvelle offre
              </Button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {stats.map((stat, index) => (
                <Card
                  key={stat.title}
                  className="hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700"
                >
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center`}>
                        <stat.icon className="w-6 h-6 text-white" />
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-green-600 dark:text-green-400">{stat.change}</div>
                        <div className="text-xs text-gray-500">{stat.changeLabel}</div>
                      </div>
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{stat.value}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{stat.title}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <input
                        type="text"
                        placeholder="Rechercher par titre ou département..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <select
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value)}
                      className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="all">Tous les statuts</option>
                      <option value="active">Active</option>
                      <option value="paused">En pause</option>
                      <option value="closed">Fermée</option>
                      <option value="draft">Brouillon</option>
                    </select>
                    <Button variant="outline">
                      <Filter className="w-4 h-4 mr-2" />
                      Filtres
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Jobs List */}
            <div className="space-y-4">
              {filteredJobs.map((job) => (
                <Card key={job.id} className="hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">{job.title}</h3>
                            <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                              <div className="flex items-center">
                                <Briefcase className="w-4 h-4 mr-1" />
                                {job.department}
                              </div>
                              <div className="flex items-center">
                                <MapPin className="w-4 h-4 mr-1" />
                                {job.location}
                              </div>
                              <div className="flex items-center">
                                <Clock className="w-4 h-4 mr-1" />
                                {job.type}
                              </div>
                              <div className="flex items-center">
                                <DollarSign className="w-4 h-4 mr-1" />
                                {job.salary.min.toLocaleString()} - {job.salary.max.toLocaleString()}{" "}
                                {job.salary.currency}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span
                              className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}
                            >
                              {getStatusText(job.status)}
                            </span>
                            <button className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                              <MoreVertical className="w-4 h-4 text-gray-400" />
                            </button>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-900 dark:text-white">{job.applicants}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">Candidatures</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-900 dark:text-white">{job.views}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">Vues</div>
                          </div>
                          <div className="text-center">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {new Date(job.createdAt).toLocaleDateString("fr-FR")}
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">Créée le</div>
                          </div>
                          <div className="text-center">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {new Date(job.deadline).toLocaleDateString("fr-FR")}
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">Échéance</div>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            {new Date(job.deadline) < new Date() && job.status === "active" && (
                              <div className="flex items-center text-red-600 dark:text-red-400 text-sm">
                                <AlertCircle className="w-4 h-4 mr-1" />
                                Échéance dépassée
                              </div>
                            )}
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button variant="outline" size="sm" onClick={() => navigate(`/jobs/${job.id}`)}>
                              <Eye className="w-4 h-4 mr-1" />
                              Voir
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => navigate(`/jobs/${job.id}/edit`)}>
                              <Edit className="w-4 h-4 mr-1" />
                              Modifier
                            </Button>
                            <Button variant="outline" size="sm">
                              <Users className="w-4 h-4 mr-1" />
                              Candidats ({job.applicants})
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {filteredJobs.length === 0 && (
              <Card className="hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700">
                <CardContent className="p-12 text-center">
                  <Briefcase className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Aucune offre trouvée</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {searchTerm || statusFilter !== "all"
                      ? "Aucune offre ne correspond à vos critères de recherche."
                      : "Vous n'avez pas encore créé d'offres d'emploi."}
                  </p>
                  <Button onClick={() => navigate("/jobs/create")}>
                    <Plus className="w-4 h-4 mr-2" />
                    Créer votre première offre
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

export default JobsPage
