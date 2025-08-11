"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import { useToast } from "../contexts/ToastContext"
import Header from "../components/Layout/Header"
import Sidebar from "../components/Layout/Sidebar"                                                                                              
import { Button } from "../components/ui/button"
import { Card, CardContent } from "../components/ui/card"
import {
  Search,
  Filter,
  Download,
  Upload,
  MoreVertical,
  Eye,
  MessageSquare,
  Star,
  Users,
  TrendingUp,
  Brain,
  MapPin,
  Briefcase,
  GraduationCap,
  Calendar,
  Phone,
  Mail,
  FileText,
} from "lucide-react"
import { useNavigate } from "react-router-dom"

interface Candidate {
  id: string
  name: string
  email: string
  phone: string
  location: string
  position: string
  experience: number
  education: string
  skills: string[]
  status: "new" | "reviewed" | "interviewed" | "hired" | "rejected"
  matchScore: number
  appliedJobs: string[]
  appliedDate: string
  lastActivity: string
  avatar: string
  resume: string
  notes: string
}

const CandidatesPage: React.FC = () => {
  const { user } = useAuth()
  const { addToast } = useToast()
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [skillFilter, setSkillFilter] = useState<string>("all")
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>([])

  const navigate = useNavigate()

  useEffect(() => {
    fetchCandidates()
  }, [])

  const fetchCandidates = async () => {
    setLoading(true)
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      const mockCandidates: Candidate[] = [
        {
          id: "1",
          name: "Sarah Alami",
          email: "sarah.alami@email.com",
          phone: "+212 6XX XX XX XX",
          location: "Casablanca",
          position: "Développeuse Full Stack",
          experience: 4,
          education: "Master Informatique",
          skills: ["React", "Node.js", "MongoDB", "TypeScript", "AWS"],
          status: "new",
          matchScore: 96,
          appliedJobs: ["Développeur Full Stack React/Node.js"],
          appliedDate: "2024-01-20",
          lastActivity: "2024-01-20",
          avatar: "/placeholder.svg?height=40&width=40&text=SA",
          resume: "sarah_alami_cv.pdf",
          notes: "",
        },
        {
          id: "2",
          name: "Ahmed Benali",
          email: "ahmed.benali@email.com",
          phone: "+212 6XX XX XX XX",
          location: "Rabat",
          position: "Chef de Projet",
          experience: 6,
          education: "Master Management",
          skills: ["Gestion de projet", "Scrum", "Leadership", "Marketing Digital"],
          status: "reviewed",
          matchScore: 89,
          appliedJobs: ["Chef de Projet Digital"],
          appliedDate: "2024-01-18",
          lastActivity: "2024-01-19",
          avatar: "/placeholder.svg?height=40&width=40&text=AB",
          resume: "ahmed_benali_cv.pdf",
          notes: "Profil très intéressant, expérience solide",
        },
        {
          id: "3",
          name: "Fatima El Mansouri",
          email: "fatima.elmansouri@email.com",
          phone: "+212 6XX XX XX XX",
          location: "Casablanca",
          position: "Data Scientist",
          experience: 3,
          education: "PhD Mathématiques",
          skills: ["Python", "Machine Learning", "TensorFlow", "SQL", "R"],
          status: "interviewed",
          matchScore: 94,
          appliedJobs: ["Data Scientist"],
          appliedDate: "2024-01-15",
          lastActivity: "2024-01-22",
          avatar: "/placeholder.svg?height=40&width=40&text=FE",
          resume: "fatima_elmansouri_cv.pdf",
          notes: "Excellent entretien technique, très motivée",
        },
        {
          id: "4",
          name: "Youssef Tazi",
          email: "youssef.tazi@email.com",
          phone: "+212 6XX XX XX XX",
          location: "Marrakech",
          position: "Stagiaire Marketing",
          experience: 0,
          education: "Licence Marketing",
          skills: ["Réseaux sociaux", "Google Analytics", "Photoshop", "Communication"],
          status: "new",
          matchScore: 78,
          appliedJobs: ["Stagiaire Marketing Digital"],
          appliedDate: "2024-01-22",
          lastActivity: "2024-01-22",
          avatar: "/placeholder.svg?height=40&width=40&text=YT",
          resume: "youssef_tazi_cv.pdf",
          notes: "",
        },
        {
          id: "5",
          name: "Khadija Alaoui",
          email: "khadija.alaoui@email.com",
          phone: "+212 6XX XX XX XX",
          location: "Fès",
          position: "UX Designer",
          experience: 5,
          education: "Master Design",
          skills: ["Figma", "Adobe XD", "User Research", "Prototyping", "UI/UX"],
          status: "hired",
          matchScore: 92,
          appliedJobs: ["UX/UI Designer"],
          appliedDate: "2024-01-10",
          lastActivity: "2024-01-25",
          avatar: "/placeholder.svg?height=40&width=40&text=KA",
          resume: "khadija_alaoui_cv.pdf",
          notes: "Embauchée - Excellent profil créatif",
        },
      ]

      setCandidates(mockCandidates)
    } catch (error) {
      addToast("Erreur lors du chargement des candidats", "error")
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: Candidate["status"]) => {
    switch (status) {
      case "new":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
      case "reviewed":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
      case "interviewed":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
      case "hired":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      case "rejected":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getStatusText = (status: Candidate["status"]) => {
    switch (status) {
      case "new":
        return "Nouveau"
      case "reviewed":
        return "Examiné"
      case "interviewed":
        return "Entretien"
      case "hired":
        return "Embauché"
      case "rejected":
        return "Rejeté"
      default:
        return status
    }
  }

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600 dark:text-green-400"
    if (score >= 75) return "text-yellow-600 dark:text-yellow-400"
    return "text-red-600 dark:text-red-400"
  }

  const filteredCandidates = candidates.filter((candidate) => {
    const matchesSearch =
      candidate.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      candidate.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
      candidate.skills.some((skill) => skill.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesStatus = statusFilter === "all" || candidate.status === statusFilter
    const matchesSkill =
      skillFilter === "all" || candidate.skills.some((skill) => skill.toLowerCase().includes(skillFilter.toLowerCase()))
    return matchesSearch && matchesStatus && matchesSkill
  })

  const stats = [
    {
      title: "Total Candidats",
      value: candidates.length.toString(),
      change: "+12",
      changeLabel: "cette semaine",
      icon: Users,
      color: "bg-blue-500",
    },
    {
      title: "Nouveaux",
      value: candidates.filter((c) => c.status === "new").length.toString(),
      change: "+5",
      changeLabel: "aujourd'hui",
      icon: TrendingUp,
      color: "bg-green-500",
    },
    {
      title: "Score Moyen IA",
      value: Math.round(candidates.reduce((sum, c) => sum + c.matchScore, 0) / candidates.length).toString() + "%",
      change: "+3%",
      changeLabel: "vs mois dernier",
      icon: Brain,
      color: "bg-purple-500",
    },
    {
      title: "Embauches",
      value: candidates.filter((c) => c.status === "hired").length.toString(),
      change: "+2",
      changeLabel: "ce mois",
      icon: Star,
      color: "bg-orange-500",
    },
  ]

  const allSkills = Array.from(new Set(candidates.flatMap((c) => c.skills)))

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      
      <div className="flex">
        
        
          <div className="p-6 y-6" >
            {/* Header */}
            <div className="flex justify-between items-center mb-8">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Candidats</h1>
                <p className="text-gray-600 dark:text-gray-400">
                  Gérez votre base de talents et suivez les candidatures
                </p>
              </div>
              <div className="flex space-x-3">
                <Button variant="outline">
                  <Upload className="w-4 h-4 mr-2" />
                  Importer CVs
                </Button>
                <Button variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Exporter
                </Button>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {stats.map((stat, index) => (
                <Card key={stat.title}>
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
                        placeholder="Rechercher par nom, poste ou compétences..."
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
                      <option value="new">Nouveau</option>
                      <option value="reviewed">Examiné</option>
                      <option value="interviewed">Entretien</option>
                      <option value="hired">Embauché</option>
                      <option value="rejected">Rejeté</option>
                    </select>
                    <select
                      value={skillFilter}
                      onChange={(e) => setSkillFilter(e.target.value)}
                      className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="all">Toutes les compétences</option>
                      {allSkills.map((skill) => (
                        <option key={skill} value={skill}>
                          {skill}
                        </option>
                      ))}
                    </select>
                    <Button variant="outline">
                      <Filter className="w-4 h-4 mr-2" />
                      Filtres avancés
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Candidates List */}
            <div className="space-y-4">
              {filteredCandidates.map((candidate) => (
                <Card
                  key={candidate.id}
                  className="hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700"
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <img
                          src={candidate.avatar || "/placeholder.svg"}
                          alt={candidate.name}
                          className="w-12 h-12 rounded-full object-cover"
                        />
                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                                {candidate.name}
                              </h3>
                              <p className="text-gray-600 dark:text-gray-400 mb-2">{candidate.position}</p>
                              <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                                <div className="flex items-center">
                                  <MapPin className="w-4 h-4 mr-1" />
                                  {candidate.location}
                                </div>
                                <div className="flex items-center">
                                  <Briefcase className="w-4 h-4 mr-1" />
                                  {candidate.experience} ans d'exp.
                                </div>
                                <div className="flex items-center">
                                  <GraduationCap className="w-4 h-4 mr-1" />
                                  {candidate.education}
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-3">
                              <div className="text-right">
                                <div className={`text-2xl font-bold ${getMatchScoreColor(candidate.matchScore)}`}>
                                  {candidate.matchScore}%
                                </div>
                                <div className="text-xs text-gray-500">Match IA</div>
                              </div>
                              <span
                                className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(candidate.status)}`}
                              >
                                {getStatusText(candidate.status)}
                              </span>
                              <button className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                                <MoreVertical className="w-4 h-4 text-gray-400" />
                              </button>
                            </div>
                          </div>

                          {/* Skills */}
                          <div className="mb-4">
                            <div className="flex flex-wrap gap-2">
                              {candidate.skills.slice(0, 5).map((skill, index) => (
                                <span
                                  key={index}
                                  className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded text-xs"
                                >
                                  {skill}
                                </span>
                              ))}
                              {candidate.skills.length > 5 && (
                                <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded text-xs">
                                  +{candidate.skills.length - 5} autres
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Contact & Actions */}
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                              <div className="flex items-center">
                                <Mail className="w-4 h-4 mr-1" />
                                {candidate.email}
                              </div>
                              <div className="flex items-center">
                                <Phone className="w-4 h-4 mr-1" />
                                {candidate.phone}
                              </div>
                              <div className="flex items-center">
                                <Calendar className="w-4 h-4 mr-1" />
                                Postulé le {new Date(candidate.appliedDate).toLocaleDateString("fr-FR")}
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => navigate(`/candidates/${candidate.id}`)}
                              >
                                <Eye className="w-4 h-4 mr-1" />
                                Profil
                              </Button>
                              <Button variant="outline" size="sm">
                                <FileText className="w-4 h-4 mr-1" />
                                CV
                              </Button>
                              <Button variant="outline" size="sm">
                                <MessageSquare className="w-4 h-4 mr-1" />
                                Message
                              </Button>
                            </div>
                          </div>

                          {/* Applied Jobs */}
                          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                              <span className="font-medium">Candidature(s) :</span>
                              {candidate.appliedJobs.map((job, index) => (
                                <span key={index} className="ml-2 text-purple-600 dark:text-purple-400">
                                  {job}
                                  {index < candidate.appliedJobs.length - 1 && ", "}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {filteredCandidates.length === 0 && (
              <Card>
                <CardContent className="p-12 text-center">
                  <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Aucun candidat trouvé</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {searchTerm || statusFilter !== "all" || skillFilter !== "all"
                      ? "Aucun candidat ne correspond à vos critères de recherche."
                      : "Vous n'avez pas encore de candidats dans votre base."}
                  </p>
                  <Button>
                    <Upload className="w-4 h-4 mr-2" />
                    Importer des CVs
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        
      </div>
    </div>
  )
}

export default CandidatesPage
