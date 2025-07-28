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
import {
  ArrowLeft,
  Phone,
  Mail,
  MapPin,
  Briefcase,
  GraduationCap,
  Calendar,
  Download,
  MessageSquare,
  Star,
  Eye,
  ExternalLink,
  Github,
  Linkedin,
  Globe,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  User,
  Brain,
  Activity,
} from "lucide-react"

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
  appliedJobs: Array<{
    id: string
    title: string
    appliedDate: string
    status: string
  }>
  appliedDate: string
  lastActivity: string
  avatar: string
  resume: string
  portfolio?: string
  linkedin?: string
  github?: string
  website?: string
  summary: string
  languages: string[]
  certifications: string[]
  notes: Array<{
    id: string
    content: string
    author: string
    date: string
    type: "note" | "interview" | "call" | "email"
  }>
  timeline: Array<{
    id: string
    type: "application" | "review" | "interview" | "call" | "email" | "status_change"
    title: string
    description: string
    date: string
    author?: string
  }>
}

const ViewCandidatePage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<"overview" | "notes" | "timeline">("overview")
  const [newNote, setNewNote] = useState("")
  const [addingNote, setAddingNote] = useState(false)

  useEffect(() => {
    fetchCandidate()
  }, [id])

  const fetchCandidate = async () => {
    setLoading(true)
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Mock candidate data
      const mockCandidate: Candidate = {
        id: id || "1",
        name: "Sarah Alami",
        email: "sarah.alami@email.com",
        phone: "+212 6XX XX XX XX",
        location: "Casablanca",
        position: "Développeuse Full Stack",
        experience: 4,
        education: "Master Informatique - ENSIAS",
        skills: ["React", "Node.js", "MongoDB", "TypeScript", "AWS", "Docker", "Git", "Python"],
        status: "reviewed",
        matchScore: 96,
        appliedJobs: [
          {
            id: "1",
            title: "Développeur Full Stack React/Node.js",
            appliedDate: "2024-01-20",
            status: "En cours",
          },
          {
            id: "2",
            title: "Lead Developer",
            appliedDate: "2024-01-15",
            status: "Rejetée",
          },
        ],
        appliedDate: "2024-01-20",
        lastActivity: "2024-01-22",
        avatar: "/placeholder.svg?height=80&width=80&text=SA",
        resume: "sarah_alami_cv.pdf",
        portfolio: "https://sarah-alami.dev",
        linkedin: "https://linkedin.com/in/sarah-alami",
        github: "https://github.com/sarah-alami",
        summary: `Développeuse Full Stack passionnée avec 4 ans d'expérience dans le développement d'applications web modernes. Spécialisée dans l'écosystème JavaScript (React, Node.js) avec une forte expertise en bases de données et déploiement cloud.

Expérience significative dans le développement d'applications e-commerce, plateformes SaaS et APIs REST. Adepte des méthodologies Agile et du travail en équipe.`,
        languages: ["Français (Natif)", "Anglais (Courant)", "Arabe (Natif)"],
        certifications: ["AWS Solutions Architect", "MongoDB Developer", "Scrum Master"],
        notes: [
          {
            id: "1",
            content: "Excellent profil technique, très motivée. Expérience solide en React et Node.js.",
            author: "Ahmed Benali",
            date: "2024-01-21",
            type: "note",
          },
          {
            id: "2",
            content: "Entretien téléphonique très positif. Bonne communication, questions pertinentes.",
            author: "Fatima El Mansouri",
            date: "2024-01-22",
            type: "call",
          },
        ],
        timeline: [
          {
            id: "1",
            type: "application",
            title: "Candidature reçue",
            description: "Candidature pour le poste de Développeur Full Stack React/Node.js",
            date: "2024-01-20",
          },
          {
            id: "2",
            type: "review",
            title: "CV examiné",
            description: "Profil technique correspondant aux exigences",
            date: "2024-01-21",
            author: "Ahmed Benali",
          },
          {
            id: "3",
            type: "call",
            title: "Entretien téléphonique",
            description: "Premier contact téléphonique - 30 minutes",
            date: "2024-01-22",
            author: "Fatima El Mansouri",
          },
          {
            id: "4",
            type: "status_change",
            title: "Statut mis à jour",
            description: "Statut changé de 'Nouveau' à 'Examiné'",
            date: "2024-01-22",
            author: "Ahmed Benali",
          },
        ],
      }

      setCandidate(mockCandidate)
    } catch (error) {
      addToast("Erreur lors du chargement du candidat", "error")
      navigate("/candidates")
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (newStatus: Candidate["status"]) => {
    if (!candidate) return

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500))

      setCandidate({ ...candidate, status: newStatus })
      addToast("Statut mis à jour avec succès", "success")
    } catch (error) {
      addToast("Erreur lors de la mise à jour", "error")
    }
  }

  const handleAddNote = async () => {
    if (!newNote.trim() || !candidate) return

    setAddingNote(true)
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500))

      const note = {
        id: Date.now().toString(),
        content: newNote,
        author: user?.name || "Utilisateur",
        date: new Date().toISOString().split("T")[0],
        type: "note" as const,
      }

      setCandidate({
        ...candidate,
        notes: [note, ...candidate.notes],
      })

      setNewNote("")
      addToast("Note ajoutée avec succès", "success")
    } catch (error) {
      addToast("Erreur lors de l'ajout de la note", "error")
    } finally {
      setAddingNote(false)
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

  const getTimelineIcon = (type: string) => {
    switch (type) {
      case "application":
        return <FileText className="w-4 h-4" />
      case "review":
        return <Eye className="w-4 h-4" />
      case "interview":
        return <MessageSquare className="w-4 h-4" />
      case "call":
        return <Phone className="w-4 h-4" />
      case "email":
        return <Mail className="w-4 h-4" />
      case "status_change":
        return <Activity className="w-4 h-4" />
      default:
        return <Clock className="w-4 h-4" />
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

  if (!candidate) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 ml-64 pt-16">
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Candidat introuvable</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">Ce candidat n'existe pas ou a été supprimé.</p>
                <Button onClick={() => navigate("/candidates")}>Retour aux candidats</Button>
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
                <Button variant="outline" onClick={() => navigate("/candidates")} className="flex items-center">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Retour
                </Button>
                <div className="flex items-center space-x-4">
                  <img
                    src={candidate.avatar || "/placeholder.svg"}
                    alt={candidate.name}
                    className="w-16 h-16 rounded-full object-cover"
                  />
                  <div>
                    <div className="flex items-center space-x-3 mb-2">
                      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{candidate.name}</h1>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(candidate.status)}`}
                      >
                        {getStatusText(candidate.status)}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400">{candidate.position}</p>
                  </div>
                </div>
              </div>
              <div className="flex space-x-3">
                <Button variant="outline">
                  <Phone className="w-4 h-4 mr-2" />
                  Appeler
                </Button>
                <Button variant="outline">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Message
                </Button>
                <Button variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  CV
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Content */}
              <div className="lg:col-span-2 space-y-6">
                {/* Tabs */}
                <div className="border-b border-gray-200 dark:border-gray-700">
                  <nav className="-mb-px flex space-x-8">
                    {[
                      { id: "overview", label: "Vue d'ensemble", icon: User },
                      { id: "notes", label: "Notes", icon: FileText },
                      { id: "timeline", label: "Timeline", icon: Clock },
                    ].map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                          activeTab === tab.id
                            ? "border-purple-500 text-purple-600 dark:text-purple-400"
                            : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                        }`}
                      >
                        <tab.icon className="w-4 h-4" />
                        <span>{tab.label}</span>
                      </button>
                    ))}
                  </nav>
                </div>

                {/* Tab Content */}
                {activeTab === "overview" && (
                  <div className="space-y-6">
                    {/* Contact & Basic Info */}
                    <Card className="dark:bg-gray-800 dark:border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-gray-900 dark:text-white">Informations de contact</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="space-y-4">
                            <div className="flex items-center space-x-3">
                              <Mail className="w-5 h-5 text-gray-400" />
                              <div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">Email</div>
                                <div className="font-medium text-gray-900 dark:text-white">{candidate.email}</div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-3">
                              <Phone className="w-5 h-5 text-gray-400" />
                              <div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">Téléphone</div>
                                <div className="font-medium text-gray-900 dark:text-white">{candidate.phone}</div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-3">
                              <MapPin className="w-5 h-5 text-gray-400" />
                              <div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">Localisation</div>
                                <div className="font-medium text-gray-900 dark:text-white">{candidate.location}</div>
                              </div>
                            </div>
                          </div>
                          <div className="space-y-4">
                            <div className="flex items-center space-x-3">
                              <Briefcase className="w-5 h-5 text-gray-400" />
                              <div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">Expérience</div>
                                <div className="font-medium text-gray-900 dark:text-white">
                                  {candidate.experience} ans
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-3">
                              <GraduationCap className="w-5 h-5 text-gray-400" />
                              <div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">Formation</div>
                                <div className="font-medium text-gray-900 dark:text-white">{candidate.education}</div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-3">
                              <Calendar className="w-5 h-5 text-gray-400" />
                              <div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">Candidature</div>
                                <div className="font-medium text-gray-900 dark:text-white">
                                  {new Date(candidate.appliedDate).toLocaleDateString("fr-FR")}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Links */}
                    {(candidate.portfolio || candidate.linkedin || candidate.github || candidate.website) && (
                      <Card className="dark:bg-gray-800 dark:border-gray-700">
                        <CardHeader>
                          <CardTitle className="text-gray-900 dark:text-white">Liens</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="flex flex-wrap gap-4">
                            {candidate.portfolio && (
                              <a
                                href={candidate.portfolio}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center space-x-2 px-3 py-2 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-800 transition-colors"
                              >
                                <Globe className="w-4 h-4" />
                                <span>Portfolio</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                            {candidate.linkedin && (
                              <a
                                href={candidate.linkedin}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center space-x-2 px-3 py-2 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
                              >
                                <Linkedin className="w-4 h-4" />
                                <span>LinkedIn</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                            {candidate.github && (
                              <a
                                href={candidate.github}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center space-x-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                              >
                                <Github className="w-4 h-4" />
                                <span>GitHub</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Summary */}
                    <Card className="dark:bg-gray-800 dark:border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-gray-900 dark:text-white">Résumé professionnel</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="prose dark:prose-invert max-w-none">
                          <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line">{candidate.summary}</p>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Skills */}
                    <Card className="dark:bg-gray-800 dark:border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-gray-900 dark:text-white">Compétences</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2">
                          {candidate.skills.map((skill, index) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-full text-sm"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Languages & Certifications */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <Card className="dark:bg-gray-800 dark:border-gray-700">
                        <CardHeader>
                          <CardTitle className="text-gray-900 dark:text-white">Langues</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            {candidate.languages.map((language, index) => (
                              <div key={index} className="text-gray-700 dark:text-gray-300">
                                {language}
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>

                      <Card className="dark:bg-gray-800 dark:border-gray-700">
                        <CardHeader>
                          <CardTitle className="text-gray-900 dark:text-white">Certifications</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            {candidate.certifications.map((cert, index) => (
                              <div key={index} className="flex items-center space-x-2">
                                <CheckCircle className="w-4 h-4 text-green-500" />
                                <span className="text-gray-700 dark:text-gray-300">{cert}</span>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    {/* Applied Jobs */}
                    <Card className="dark:bg-gray-800 dark:border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-gray-900 dark:text-white">Candidatures</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {candidate.appliedJobs.map((job, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                            >
                              <div>
                                <h4 className="font-medium text-gray-900 dark:text-white">{job.title}</h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  Candidature le {new Date(job.appliedDate).toLocaleDateString("fr-FR")}
                                </p>
                              </div>
                              <span
                                className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  job.status === "En cours"
                                    ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                                    : job.status === "Rejetée"
                                      ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                                      : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                                }`}
                              >
                                {job.status}
                              </span>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}

                {activeTab === "notes" && (
                  <div className="space-y-6">
                    {/* Add Note */}
                    <Card className="dark:bg-gray-800 dark:border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-gray-900 dark:text-white">Ajouter une note</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <textarea
                            value={newNote}
                            onChange={(e) => setNewNote(e.target.value)}
                            rows={4}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            placeholder="Ajouter une note sur ce candidat..."
                          />
                          <Button onClick={handleAddNote} disabled={!newNote.trim() || addingNote}>
                            {addingNote ? "Ajout..." : "Ajouter la note"}
                          </Button>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Notes List */}
                    <div className="space-y-4">
                      {candidate.notes.map((note) => (
                        <Card key={note.id} className="dark:bg-gray-800 dark:border-gray-700">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center space-x-2">
                                <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                                  {note.type === "note" && (
                                    <FileText className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                  )}
                                  {note.type === "call" && (
                                    <Phone className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                  )}
                                  {note.type === "email" && (
                                    <Mail className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                  )}
                                  {note.type === "interview" && (
                                    <MessageSquare className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                  )}
                                </div>
                                <div>
                                  <div className="font-medium text-gray-900 dark:text-white">{note.author}</div>
                                  <div className="text-sm text-gray-600 dark:text-gray-400">
                                    {new Date(note.date).toLocaleDateString("fr-FR")}
                                  </div>
                                </div>
                              </div>
                            </div>
                            <p className="text-gray-700 dark:text-gray-300">{note.content}</p>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === "timeline" && (
                  <div className="space-y-6">
                    <Card className="dark:bg-gray-800 dark:border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-gray-900 dark:text-white">Historique des activités</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-6">
                          {candidate.timeline.map((event, index) => (
                            <div key={event.id} className="flex items-start space-x-4">
                              <div className="flex-shrink-0">
                                <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                                  {getTimelineIcon(event.type)}
                                </div>
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between">
                                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">{event.title}</h4>
                                  <span className="text-sm text-gray-500 dark:text-gray-400">
                                    {new Date(event.date).toLocaleDateString("fr-FR")}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{event.description}</p>
                                {event.author && (
                                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">Par {event.author}</p>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Match Score */}
                <Card className="dark:bg-gray-800 dark:border-gray-700">
                  <CardHeader>
                    <CardTitle className="flex items-center text-gray-900 dark:text-white">
                      <Brain className="w-5 h-5 mr-2" />
                      Score IA
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center">
                      <div className={`text-4xl font-bold mb-2 ${getMatchScoreColor(candidate.matchScore)}`}>
                        {candidate.matchScore}%
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Compatibilité avec le poste</p>
                    </div>
                  </CardContent>
                </Card>

                {/* Status Actions */}
                <Card className="dark:bg-gray-800 dark:border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-gray-900 dark:text-white">Changer le statut</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button
                      variant={candidate.status === "reviewed" ? "default" : "outline"}
                      className="w-full justify-start"
                      onClick={() => handleStatusChange("reviewed")}
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      Marquer comme examiné
                    </Button>
                    <Button
                      variant={candidate.status === "interviewed" ? "default" : "outline"}
                      className="w-full justify-start"
                      onClick={() => handleStatusChange("interviewed")}
                    >
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Programmer entretien
                    </Button>
                    <Button
                      variant={candidate.status === "hired" ? "default" : "outline"}
                      className="w-full justify-start bg-green-600 hover:bg-green-700 text-white"
                      onClick={() => handleStatusChange("hired")}
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Embaucher
                    </Button>
                    <Button
                      variant={candidate.status === "rejected" ? "default" : "outline"}
                      className="w-full justify-start text-red-600 border-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                      onClick={() => handleStatusChange("rejected")}
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Rejeter
                    </Button>
                  </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card className="dark:bg-gray-800 dark:border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-gray-900 dark:text-white">Actions rapides</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      <Phone className="w-4 h-4 mr-2" />
                      Appeler
                    </Button>
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Envoyer un message
                    </Button>
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      <Download className="w-4 h-4 mr-2" />
                      Télécharger CV
                    </Button>
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      <Star className="w-4 h-4 mr-2" />
                      Ajouter aux favoris
                    </Button>
                  </CardContent>
                </Card>

                {/* Activity Summary */}
                <Card className="dark:bg-gray-800 dark:border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-gray-900 dark:text-white">Résumé d'activité</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Candidatures</span>
                      <span className="font-medium text-gray-900 dark:text-white">{candidate.appliedJobs.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Notes</span>
                      <span className="font-medium text-gray-900 dark:text-white">{candidate.notes.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Dernière activité</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {new Date(candidate.lastActivity).toLocaleDateString("fr-FR")}
                      </span>
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

export default ViewCandidatePage
