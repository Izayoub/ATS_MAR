"use client"

import { useState, useEffect } from "react"
import { Search, Settings, Target, TrendingUp, Users, Briefcase, Filter, ArrowLeft } from "lucide-react"
import { Button } from "../components/ui/button"
import { Card, CardContent } from "../components/ui/card"
import { useNavigate } from "react-router-dom"
import { API_ENDPOINTS } from "../config/api"

interface MatchingCriteria {
  skills: number
  experience: number
  education: number
  location: number
  description: number
}

interface MatchResult {
  candidate_id: number
  job_id: number
  overall_score: number
  recommendation: string
  field_matches: Array<{
    field_name: string
    similarity_score: number
    confidence: string
    candidate_value: any
    job_value: any
  }>
  candidate_name?: string
  job_title?: string
}

export default function MatchingPage() {
  const navigate = useNavigate()
  const [candidates, setCandidates] = useState([])
  const [jobs, setJobs] = useState([])
  const [selectedCandidate, setSelectedCandidate] = useState<number | null>(null)
  const [selectedJob, setSelectedJob] = useState<number | null>(null)
  const [matchResults, setMatchResults] = useState<MatchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [showCriteria, setShowCriteria] = useState(false)
  const [criteria, setCriteria] = useState<MatchingCriteria>({
    skills: 30,
    experience: 25,
    education: 20,
    location: 10,
    description: 15,
  })

  useEffect(() => {
    fetchCandidates()
    fetchJobs()
  }, [])

  const fetchCandidates = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.CANDIDATES)
      const data = await response.json()
      setCandidates(data.results || data)
    } catch (error) {
      console.error("Erreur fetch candidats:", error)
    }
  }

  const fetchJobs = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.JOBS)
      const data = await response.json()
      setJobs(data.results || data)
    } catch (error) {
      console.error("Erreur fetch jobs:", error)
    }
  }

  const runMatching = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (selectedCandidate) params.append("candidate_id", selectedCandidate.toString())
      if (selectedJob) params.append("job_id", selectedJob.toString())

      Object.entries(criteria).forEach(([key, value]) => {
        params.append(`weight_${key}`, (value / 100).toString())
      })

      const endpoint = selectedCandidate
        ? API_ENDPOINTS.CANDIDATE_MATCHING(selectedCandidate)
        : selectedJob
          ? API_ENDPOINTS.JOB_MATCHING(selectedJob)
          : "/api/matching/"

      const response = await fetch(`${endpoint}?${params}`)
      const data = await response.json()
      setMatchResults(data.matches || [])
    } catch (error) {
      console.error("Erreur matching:", error)
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "text-green-600 bg-green-100"
    if (score >= 0.6) return "text-blue-600 bg-blue-100"
    if (score >= 0.4) return "text-yellow-600 bg-yellow-100"
    return "text-red-600 bg-red-100"
  }

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case "excellent":
        return "bg-green-500"
      case "good":
        return "bg-blue-500"
      case "fair":
        return "bg-yellow-500"
      default:
        return "bg-red-500"
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="outline" onClick={() => navigate("/candidates")}>
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                  <Target className="h-8 w-8 text-blue-600" />
                  Matching IA
                </h1>
                <p className="text-gray-600 mt-2">
                  Analysez la compatibilité entre candidats et offres d'emploi avec des critères personnalisables
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowCriteria(!showCriteria)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <Settings className="h-5 w-5" />
              Critères
            </button>
          </div>
        </div>

        {/* Critères de matching */}
        {showCriteria && (
          <Card className="mb-6">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Filter className="h-5 w-5" />
                Configuration des critères de matching
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {Object.entries(criteria).map(([key, value]) => (
                  <div key={key} className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700 capitalize">
                      {key === "skills"
                        ? "Compétences"
                        : key === "experience"
                          ? "Expérience"
                          : key === "education"
                            ? "Formation"
                            : key === "location"
                              ? "Localisation"
                              : "Description"}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="50"
                      value={value}
                      onChange={(e) =>
                        setCriteria((prev) => ({
                          ...prev,
                          [key]: Number.parseInt(e.target.value),
                        }))
                      }
                      className="w-full"
                    />
                    <div className="text-center text-sm text-gray-600">{value}%</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Sélection */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Candidats */}
          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Users className="h-6 w-6 text-blue-600" />
                Sélectionner un candidat
              </h2>
              <select
                value={selectedCandidate || ""}
                onChange={(e) => setSelectedCandidate(e.target.value ? Number.parseInt(e.target.value) : null)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Tous les candidats</option>
                {candidates.map((candidate: any) => (
                  <option key={candidate.id} value={candidate.id}>
                    {candidate.first_name} {candidate.last_name} - {candidate.email}
                  </option>
                ))}
              </select>
            </CardContent>
          </Card>

          {/* Jobs */}
          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Briefcase className="h-6 w-6 text-green-600" />
                Sélectionner une offre
              </h2>
              <select
                value={selectedJob || ""}
                onChange={(e) => setSelectedJob(e.target.value ? Number.parseInt(e.target.value) : null)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Toutes les offres</option>
                {jobs.map((job: any) => (
                  <option key={job.id} value={job.id}>
                    {job.title} - {job.company_name}
                  </option>
                ))}
              </select>
            </CardContent>
          </Card>
        </div>

        {/* Bouton de matching */}
        <div className="text-center mb-6">
          <Button
            onClick={runMatching}
            disabled={loading}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 flex items-center gap-2 mx-auto"
          >
            <Search className="h-5 w-5" />
            {loading ? "Analyse en cours..." : "Lancer le matching"}
          </Button>
        </div>

        {/* Résultats */}
        {matchResults.length > 0 && (
          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-green-600" />
                Résultats du matching ({matchResults.length})
              </h2>

              <div className="space-y-6">
                {matchResults.map((match, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold">
                          Candidat #{match.candidate_id} ↔ Job #{match.job_id}
                        </h3>
                        <div className="flex items-center gap-4 mt-2">
                          <span
                            className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(match.overall_score)}`}
                          >
                            Score: {(match.overall_score * 100).toFixed(1)}%
                          </span>
                          <span
                            className={`px-3 py-1 rounded-full text-white text-sm font-medium ${getRecommendationColor(match.recommendation)}`}
                          >
                            {match.recommendation.toUpperCase()}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Détails par critère */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                      {match.field_matches.map((field, fieldIndex) => (
                        <div key={fieldIndex} className="bg-gray-50 rounded-lg p-4">
                          <h4 className="font-medium text-gray-900 capitalize mb-2">
                            {field.field_name === "skills"
                              ? "Compétences"
                              : field.field_name === "experience"
                                ? "Expérience"
                                : field.field_name === "education"
                                  ? "Formation"
                                  : field.field_name === "location"
                                    ? "Localisation"
                                    : "Description"}
                          </h4>
                          <div className={`text-sm px-2 py-1 rounded ${getScoreColor(field.similarity_score)}`}>
                            {(field.similarity_score * 100).toFixed(1)}%
                          </div>
                          <div className="text-xs text-gray-600 mt-1">Confiance: {field.confidence}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
