"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { useToast } from "../contexts/ToastContext"
import { useCandidate } from "../hooks/useCandidate"
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
  Eye,
  ExternalLink,
  Linkedin,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  User,
  Brain,
  Activity,
  Loader2,
} from "lucide-react"
import type { Candidate } from "../types/api"

const ViewCandidatePage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const candidateId = Number.parseInt(id || "0")

  const {
    candidate,
    notes,
    timeline,
    matches,
    loading,
    error,
    notesLoading,
    timelineLoading,
    matchingLoading,
    fetchNotes,
    fetchTimeline,
    findMatches,
    updateStatus,
    addNote,
  } = useCandidate(candidateId)

  const [activeTab, setActiveTab] = useState<"overview" | "notes" | "timeline" | "matching">("overview")
  const [newNote, setNewNote] = useState("")
  const [addingNote, setAddingNote] = useState(false)

  useEffect(() => {
    if (activeTab === "notes" && notes.length === 0 && !notesLoading) {
      fetchNotes()
    }
    if (activeTab === "timeline" && timeline.length === 0 && !timelineLoading) {
      fetchTimeline()
    }
  }, [activeTab])

  const handleStatusChange = async (newStatus: Candidate["status"]) => {
    try {
      await updateStatus(newStatus)
      addToast("Statut mis à jour avec succès", "success")
    } catch (error: any) {
      addToast(error.message || "Erreur lors de la mise à jour", "error")
    }
  }

  const handleAddNote = async () => {
    if (!newNote.trim()) return

    setAddingNote(true)
    try {
      await addNote(newNote)
      setNewNote("")
      addToast("Note ajoutée avec succès", "success")
    } catch (error: any) {
      addToast(error.message || "Erreur lors de l'ajout de la note", "error")
    } finally {
      setAddingNote(false)
    }
  }

  const handleFindMatches = async () => {
    try {
      await findMatches()
      addToast("Matching terminé avec succès", "success")
    } catch (error: any) {
      addToast("Erreur lors du matching", "error")
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("fr-FR")
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 ml-64 pt-16">
            <div className="flex items-center justify-center h-96">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
                <span className="text-lg text-gray-600 dark:text-gray-400">Chargement du candidat...</span>
              </div>
            </div>
          </main>
        </div>
      </div>
    )
  }

  if (error || !candidate) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 ml-64 pt-16">
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {error || "Candidat introuvable"}
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {error || "Ce candidat n'existe pas ou a été supprimé."}
                </p>
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
                  <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                    <User className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-3 mb-2">
                      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{candidate.full_name}</h1>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(candidate.status)}`}
                      >
                        {getStatusText(candidate.status)}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400">{candidate.current_position}</p>
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
                {candidate.cv_file && (
                  <Button variant="outline" asChild>
                    <a href={candidate.cv_file} target="_blank" rel="noopener noreferrer">
                      <Download className="w-4 h-4 mr-2" />
                      CV
                    </a>
                  </Button>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Content */}
              <div className="lg:col-span-2 space-y-6">
                {/* Tabs */}
                <div className="border-b border-gray-200 dark:border-gray-700">
                  <nav className="-mb-px flex space-x-8">
                    {[
                      {
                        id: "overview",
                        label: "Vue d'ensemble",
                        icon: User,
                      },
                      { id: "notes", label: "Notes", icon: FileText },
                      { id: "timeline", label: "Timeline", icon: Clock },
                      { id: "matching", label: "Matching IA", icon: Brain },
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
                            {candidate.phone && (
                              <div className="flex items-center space-x-3">
                                <Phone className="w-5 h-5 text-gray-400" />
                                <div>
                                  <div className="text-sm text-gray-600 dark:text-gray-400">Téléphone</div>
                                  <div className="font-medium text-gray-900 dark:text-white">{candidate.phone}</div>
                                </div>
                              </div>
                            )}
                            {candidate.city && (
                              <div className="flex items-center space-x-3">
                                <MapPin className="w-5 h-5 text-gray-400" />
                                <div>
                                  <div className="text-sm text-gray-600 dark:text-gray-400">Ville</div>
                                  <div className="font-medium text-gray-900 dark:text-white">{candidate.city}</div>
                                </div>
                              </div>
                            )}
                          </div>
                          <div className="space-y-4">
                            {candidate.experience_years && (
                              <div className="flex items-center space-x-3">
                                <Briefcase className="w-5 h-5 text-gray-400" />
                                <div>
                                  <div className="text-sm text-gray-600 dark:text-gray-400">Expérience</div>
                                  <div className="font-medium text-gray-900 dark:text-white">
                                    {candidate.experience_years} ans
                                  </div>
                                </div>
                              </div>
                            )}
                            {candidate.education_level && (
                              <div className="flex items-center space-x-3">
                                <GraduationCap className="w-5 h-5 text-gray-400" />
                                <div>
                                  <div className="text-sm text-gray-600 dark:text-gray-400">Formation</div>
                                  <div className="font-medium text-gray-900 dark:text-white">
                                    {candidate.education_level}
                                  </div>
                                </div>
                              </div>
                            )}
                            <div className="flex items-center space-x-3">
                              <Calendar className="w-5 h-5 text-gray-400" />
                              <div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">Candidature</div>
                                <div className="font-medium text-gray-900 dark:text-white">
                                  {formatDate(candidate.created_at)}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Links */}
                    {candidate.linkedin_url && (
                      <Card className="dark:bg-gray-800 dark:border-gray-700">
                        <CardHeader>
                          <CardTitle className="text-gray-900 dark:text-white">Liens</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="flex flex-wrap gap-4">
                            <a
                              href={candidate.linkedin_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center space-x-2 px-3 py-2 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
                            >
                              <Linkedin className="w-4 h-4" />
                              <span>LinkedIn</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* AI Summary */}
                    {candidate.ai_summary && (
                      <Card className="dark:bg-gray-800 dark:border-gray-700">
                        <CardHeader>
                          <CardTitle className="text-gray-900 dark:text-white">Résumé IA</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="prose dark:prose-invert max-w-none">
                            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line">
                              {candidate.ai_summary}
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Skills */}
                    <Card className="dark:bg-gray-800 dark:border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-gray-900 dark:text-white">Compétences</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {candidate.technical_skills &&
                            Array.isArray(candidate.technical_skills) &&
                            candidate.technical_skills.length > 0 && (
                              <div>
                                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                                  Compétences techniques ({candidate.technical_skills.length})
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                  {candidate.technical_skills.map((skill, index) => (
                                    <span
                                      key={index}
                                      className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full dark:bg-green-900 dark:text-green-300"
                                    >
                                      {skill}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                          {candidate.soft_skills &&
                            Array.isArray(candidate.soft_skills) &&
                            candidate.soft_skills.length > 0 && (
                              <div>
                                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                                  Compétences comportementales ({candidate.soft_skills.length})
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                  {candidate.soft_skills.map((skill, index) => (
                                    <span
                                      key={index}
                                      className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full dark:bg-blue-900 dark:text-blue-300"
                                    >
                                      {skill}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                          {(!candidate.technical_skills || candidate.technical_skills.length === 0) &&
                            (!candidate.soft_skills || candidate.soft_skills.length === 0) &&
                            candidate.skills_extracted && (
                              <div>
                                {/* Si skills_extracted est un objet avec technical_skills */}
                                {typeof candidate.skills_extracted === "object" &&
                                  !Array.isArray(candidate.skills_extracted) &&
                                  candidate.skills_extracted.technical_skills &&
                                  Array.isArray(candidate.skills_extracted.technical_skills) &&
                                  candidate.skills_extracted.technical_skills.length > 0 && (
                                    <div className="mb-4">
                                      <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                                        Compétences techniques ({candidate.skills_extracted.technical_skills.length})
                                      </h4>
                                      <div className="flex flex-wrap gap-2">
                                        {candidate.skills_extracted.technical_skills.map((skill, index) => (
                                          <span
                                            key={index}
                                            className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full dark:bg-green-900 dark:text-green-300"
                                          >
                                            {skill}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  )}

                                {/* Si skills_extracted est un objet avec soft_skills */}
                                {typeof candidate.skills_extracted === "object" &&
                                  !Array.isArray(candidate.skills_extracted) &&
                                  candidate.skills_extracted.soft_skills &&
                                  Array.isArray(candidate.skills_extracted.soft_skills) &&
                                  candidate.skills_extracted.soft_skills.length > 0 && (
                                    <div>
                                      <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                                        Compétences comportementales ({candidate.skills_extracted.soft_skills.length})
                                      </h4>
                                      <div className="flex flex-wrap gap-2">
                                        {candidate.skills_extracted.soft_skills.map((skill, index) => (
                                          <span
                                            key={index}
                                            className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full dark:bg-blue-900 dark:text-blue-300"
                                          >
                                            {skill}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  )}

                                {/* Si skills_extracted est un simple array */}
                                {Array.isArray(candidate.skills_extracted) && candidate.skills_extracted.length > 0 && (
                                  <div>
                                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                                      Compétences ({candidate.skills_extracted.length})
                                    </h4>
                                    <div className="flex flex-wrap gap-2">
                                      {candidate.skills_extracted.map((skill, index) => (
                                        <span
                                          key={index}
                                          className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full dark:bg-gray-700 dark:text-gray-300"
                                        >
                                          {skill}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}

                          {(!candidate.technical_skills || candidate.technical_skills.length === 0) &&
                            (!candidate.soft_skills || candidate.soft_skills.length === 0) &&
                            (!candidate.skills_extracted ||
                              (typeof candidate.skills_extracted === "object" &&
                                !Array.isArray(candidate.skills_extracted) &&
                                (!candidate.skills_extracted.technical_skills ||
                                  candidate.skills_extracted.technical_skills.length === 0) &&
                                (!candidate.skills_extracted.soft_skills ||
                                  candidate.skills_extracted.soft_skills.length === 0)) ||
                              (Array.isArray(candidate.skills_extracted) &&
                                candidate.skills_extracted.length === 0)) && (
                              <div className="text-center py-4 text-gray-500 dark:text-gray-400">
                                Aucune compétence renseignée
                              </div>
                            )}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Languages */}
                    {candidate.languages && candidate.languages.length > 0 && (
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
                    )}
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
                            {addingNote ? (
                              <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Ajout...
                              </>
                            ) : (
                              "Ajouter la note"
                            )}
                          </Button>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Notes List */}
                    {notesLoading ? (
                      <div className="flex items-center justify-center py-8">
                        <Loader2 className="w-6 h-6 animate-spin text-purple-600" />
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {notes.map((note) => (
                          <Card key={note.id} className="dark:bg-gray-800 dark:border-gray-700">
                            <CardContent className="p-4">
                              <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center space-x-2">
                                  <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                                    {note.note_type === "note" && (
                                      <FileText className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                    )}
                                    {note.note_type === "call" && (
                                      <Phone className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                    )}
                                    {note.note_type === "email" && (
                                      <Mail className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                    )}
                                    {note.note_type === "interview" && (
                                      <MessageSquare className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                    )}
                                  </div>
                                  <div>
                                    <div className="font-medium text-gray-900 dark:text-white">
                                      {note.author.get_full_name}
                                    </div>
                                    <div className="text-sm text-gray-600 dark:text-gray-400">
                                      {formatDate(note.created_at)}
                                    </div>
                                  </div>
                                </div>
                              </div>
                              <p className="text-gray-700 dark:text-gray-300">{note.content}</p>
                            </CardContent>
                          </Card>
                        ))}
                        {notes.length === 0 && (
                          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                            Aucune note pour ce candidat
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {activeTab === "timeline" && (
                  <div className="space-y-6">
                    <Card className="dark:bg-gray-800 dark:border-gray-700">
                      <CardHeader>
                        <CardTitle className="text-gray-900 dark:text-white">Historique des activités</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {timelineLoading ? (
                          <div className="flex items-center justify-center py-8">
                            <Loader2 className="w-6 h-6 animate-spin text-purple-600" />
                          </div>
                        ) : (
                          <div className="space-y-6">
                            {timeline.map((event, index) => (
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
                                      {formatDate(event.date)}
                                    </span>
                                  </div>
                                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{event.description}</p>
                                  {event.author && (
                                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">Par {event.author}</p>
                                  )}
                                </div>
                              </div>
                            ))}
                            {timeline.length === 0 && (
                              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                                Aucune activité enregistrée
                              </div>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                )}

                {activeTab === "matching" && (
                  <div className="space-y-6">
                    <Card className="dark:bg-gray-800 dark:border-gray-700">
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between text-gray-900 dark:text-white">
                          <span>Matching IA - Offres d'emploi compatibles</span>
                          <Button onClick={handleFindMatches} disabled={matchingLoading}>
                            {matchingLoading ? (
                              <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Recherche...
                              </>
                            ) : (
                              <>
                                <Brain className="w-4 h-4 mr-2" />
                                Lancer le matching
                              </>
                            )}
                          </Button>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        {matches.length > 0 ? (
                          <div className="space-y-4">
                            {matches.map((match, index) => (
                              <div
                                key={match.job_id}
                                className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
                              >
                                <div className="flex items-center justify-between mb-3">
                                  <div>
                                    <h4 className="font-medium text-gray-900 dark:text-white">{match.job_title}</h4>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                      {match.company_name} • {match.location}
                                    </p>
                                  </div>
                                  <div className="text-right">
                                    <div className={`text-2xl font-bold ${getMatchScoreColor(match.overall_score)}`}>
                                      {match.overall_score}%
                                    </div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">Compatibilité</div>
                                  </div>
                                </div>
                                <div className="mb-3">
                                  <p className="text-sm text-gray-700 dark:text-gray-300">{match.recommendation}</p>
                                </div>
                                <div className="flex items-center justify-between text-sm">
                                  <span className="text-gray-600 dark:text-gray-400">
                                    {match.contract_type} • {match.salary_range}
                                  </span>
                                  <Button variant="outline" size="sm">
                                    Voir l'offre
                                  </Button>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                            Cliquez sur "Lancer le matching" pour trouver les offres compatibles
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                )}
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Match Score */}
                {candidate.global_match_score && (
                  <Card className="dark:bg-gray-800 dark:border-gray-700">
                    <CardHeader>
                      <CardTitle className="flex items-center text-gray-900 dark:text-white">
                        <Brain className="w-5 h-5 mr-2" />
                        Score IA Global
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center">
                        <div className={`text-4xl font-bold mb-2 ${getMatchScoreColor(candidate.global_match_score)}`}>
                          {Math.round(candidate.global_match_score)}%
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Score de compatibilité global</p>
                      </div>
                    </CardContent>
                  </Card>
                )}

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
                    {candidate.phone && (
                      <Button variant="outline" className="w-full justify-start bg-transparent" asChild>
                        <a href={`tel:${candidate.phone}`}>
                          <Phone className="w-4 h-4 mr-2" />
                          Appeler
                        </a>
                      </Button>
                    )}
                    <Button variant="outline" className="w-full justify-start bg-transparent" asChild>
                      <a href={`mailto:${candidate.email}`}>
                        <MessageSquare className="w-4 h-4 mr-2" />
                        Envoyer un email
                      </a>
                    </Button>
                    {candidate.cv_file && (
                      <Button variant="outline" className="w-full justify-start bg-transparent" asChild>
                        <a href={candidate.cv_file} target="_blank" rel="noopener noreferrer">
                          <Download className="w-4 h-4 mr-2" />
                          Télécharger CV
                        </a>
                      </Button>
                    )}
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
                      <span className="font-medium text-gray-900 dark:text-white">{candidate.application_count}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Notes</span>
                      <span className="font-medium text-gray-900 dark:text-white">{notes.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Dernière mise à jour</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {formatDate(candidate.updated_at)}
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
