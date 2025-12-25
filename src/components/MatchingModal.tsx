"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "./ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { X, Target, CheckCircle, AlertCircle, TrendingUp, Users, Briefcase, GraduationCap } from "lucide-react"
import type { Candidate } from "../types/api"
import { API_ENDPOINTS } from "../config/api"
import {apiClient} from "../services/apiClient"

interface MatchingResult {
  job_id: number
  job_title: string
  company: string
  overall_score: number
  technical_score: number
  soft_skills_score: number
  experience_score: number
  education_score: number
  recommendation: string
  matching_details: {
    matched_technical_skills: string[]
    matched_soft_skills: string[]
    missing_skills: string[]
    experience_match: string
    education_match: string
  }
}

interface MatchingModalProps {
  isOpen: boolean
  onClose: () => void
  candidate: Candidate | null
  onSuccess: (results: MatchingResult[]) => void
}

const MatchingModal: React.FC<MatchingModalProps> = ({ isOpen, onClose, candidate, onSuccess }) => {
  const [step, setStep] = useState<"confirm" | "processing" | "results">("confirm")
  const [matchingResults, setMatchingResults] = useState<MatchingResult[]>([])
  const [error, setError] = useState<string | null>(null)

  if (!isOpen || !candidate) return null

  const startMatching = async () => {
    setStep("processing")
    setError(null)

    try {
      const response = await apiClient.post(API_ENDPOINTS.CANDIDATE_MATCHING(candidate.id), {
        candidate_id: candidate.id,
      })

      const data = response.data
      setMatchingResults(data.results || [])
      setStep("results")
      onSuccess(data.results || [])
    } catch (err: any) {
      setError(err.message)
      setStep("confirm")
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-300"
    if (score >= 60) return "text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-300"
    return "text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-300"
  }

  const getRecommendationIcon = (recommendation: string) => {
    if (recommendation.toLowerCase().includes("excellent") || recommendation.toLowerCase().includes("parfait")) {
      return <CheckCircle className="h-5 w-5 text-green-600" />
    }
    if (recommendation.toLowerCase().includes("bon") || recommendation.toLowerCase().includes("convenable")) {
      return <TrendingUp className="h-5 w-5 text-yellow-600" />
    }
    return <AlertCircle className="h-5 w-5 text-red-600" />
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Target className="h-6 w-6 text-purple-600" />
            Matching IA
          </h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="p-6">
          {step === "confirm" && (
            <div className="text-center space-y-6">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-2xl mx-auto">
                {candidate.first_name[0]}
                {candidate.last_name[0]}
              </div>

              <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">{candidate.full_name}</h3>
                <p className="text-gray-600 dark:text-gray-400">{candidate.current_position}</p>
              </div>

              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">Profil du candidat</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Briefcase className="h-4 w-4 text-gray-500" />
                    <span>{candidate.experience_summary?.years || 0} ans d'expérience</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <GraduationCap className="h-4 w-4 text-gray-500" />
                    <span>{candidate.education_level}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-gray-500" />
                    <span>{candidate.skills_summary?.technical_count || 0} compétences techniques</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-gray-500" />
                    <span>{candidate.skills_summary?.soft_count || 0} compétences comportementales</span>
                  </div>
                </div>
              </div>

              {error && (
                <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4">
                  <p className="text-red-800 dark:text-red-200">{error}</p>
                </div>
              )}

              <div className="flex gap-4 justify-center">
                <Button variant="outline" onClick={onClose}>
                  Annuler
                </Button>
                <Button onClick={startMatching} className="bg-purple-600 hover:bg-purple-700">
                  Lancer le matching
                </Button>
              </div>
            </div>
          )}

          {step === "processing" && (
            <div className="text-center space-y-6 py-12">
              <div className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto"></div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Analyse en cours...</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  L'IA analyse le profil de {candidate.full_name} et compare avec toutes les offres actives
                </p>
              </div>
            </div>
          )}

          {step === "results" && (
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Résultats du matching pour {candidate.full_name}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">{matchingResults.length} offre(s) analysée(s)</p>
              </div>

              {matchingResults.length === 0 ? (
                <div className="text-center py-8">
                  <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    Aucune offre d'emploi active trouvée pour le matching
                  </p>
                </div>
              ) : (
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {matchingResults.map((result, index) => (
                    <Card key={index} className="border-l-4 border-l-purple-500">
                      <CardHeader className="pb-3">
                        <div className="flex justify-between items-start">
                          <div>
                            <CardTitle className="text-lg">{result.job_title}</CardTitle>
                            <p className="text-gray-600 dark:text-gray-400">{result.company}</p>
                          </div>
                          <div className="text-right">
                            <div
                              className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(result.overall_score)}`}
                            >
                              {Math.round(result.overall_score)}%
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-gray-500 dark:text-gray-400">Technique</p>
                            <p className="font-medium">{Math.round(result.technical_score)}%</p>
                          </div>
                          <div>
                            <p className="text-gray-500 dark:text-gray-400">Soft Skills</p>
                            <p className="font-medium">{Math.round(result.soft_skills_score)}%</p>
                          </div>
                          <div>
                            <p className="text-gray-500 dark:text-gray-400">Expérience</p>
                            <p className="font-medium">{Math.round(result.experience_score)}%</p>
                          </div>
                          <div>
                            <p className="text-gray-500 dark:text-gray-400">Formation</p>
                            <p className="font-medium">{Math.round(result.education_score)}%</p>
                          </div>
                        </div>

                        <div className="flex items-start gap-2 bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                          {getRecommendationIcon(result.recommendation)}
                          <p className="text-sm text-gray-700 dark:text-gray-300">{result.recommendation}</p>
                        </div>

                        {result.matching_details && (
                          <div className="space-y-2 text-sm">
                            {result.matching_details.matched_technical_skills.length > 0 && (
                              <div>
                                <p className="font-medium text-green-700 dark:text-green-300">
                                  Compétences techniques correspondantes:
                                </p>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {result.matching_details.matched_technical_skills.map((skill, i) => (
                                    <span
                                      key={i}
                                      className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs dark:bg-green-900 dark:text-green-300"
                                    >
                                      {skill}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                            {result.matching_details.missing_skills.length > 0 && (
                              <div>
                                <p className="font-medium text-red-700 dark:text-red-300">Compétences manquantes:</p>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {result.matching_details.missing_skills.map((skill, i) => (
                                    <span
                                      key={i}
                                      className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs dark:bg-red-900 dark:text-red-300"
                                    >
                                      {skill}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              <div className="flex justify-center">
                <Button onClick={onClose}>Fermer</Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MatchingModal
