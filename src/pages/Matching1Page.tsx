"use client"

import type React from "react"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"
import { Input } from "../components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs"
import { Users, Briefcase, Play, History, Search, Star, Calendar, TrendingUp, User, Building } from "lucide-react"
import Layout from "../components/Layout/Layout"

// Types pour les données statiques
interface Candidate {
  id: number
  name: string
  title: string
  experience: string
  skills: string[]
  location: string
  score?: number
}

interface Job {
  id: number
  title: string
  company: string
  location: string
  type: string
  requirements: string[]
}

interface CandidateGroup {
  id: number
  name: string
  count: number
  color: string
}

interface MatchingResult {
  id: number
  candidateName: string
  jobTitle: string
  score: number
  date: string
  status: "completed" | "pending" | "failed"
}

const MatchingPage: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState<"candidates" | "groups">("candidates")
  const [selectedCandidates, setSelectedCandidates] = useState<number[]>([])
  const [selectedGroups, setSelectedGroups] = useState<number[]>([])
  const [selectedJobs, setSelectedJobs] = useState<number[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isMatching, setIsMatching] = useState(false)

  // Données statiques pour la démo
  const candidateGroups: CandidateGroup[] = [
    { id: 1, name: "Développeurs Frontend", count: 15, color: "blue" },
    { id: 2, name: "Développeurs Backend", count: 12, color: "green" },
    { id: 3, name: "Data Scientists", count: 8, color: "purple" },
    { id: 4, name: "DevOps Engineers", count: 6, color: "orange" },
  ]

  const candidates: Candidate[] = [
    {
      id: 1,
      name: "Ahmed Benali",
      title: "Développeuse React",
      experience: "3 ans",
      skills: ["React", "TypeScript", "Node.js"],
      location: "Paris",
    },
    {
      id: 2,
      name: "Nour El Amrani",
      title: "Ingénieur Backend",
      experience: "5 ans",
      skills: ["Python", "Django", "PostgreSQL"],
      location: "Lyon",
    },
    {
      id: 3,
      name: "Sophie Laurent",
      title: "Data Scientist",
      experience: "4 ans",
      skills: ["Python", "Machine Learning", "SQL"],
      location: "Marseille",
    },
    {
      id: 4,
      name: "Pierre Moreau",
      title: "DevOps Engineer",
      experience: "6 ans",
      skills: ["Docker", "Kubernetes", "AWS"],
      location: "Toulouse",
    },
  ]

  const jobs: Job[] = [
    {
      id: 1,
      title: "Développeur React Senior",
      company: "TechCorp",
      location: "Paris",
      type: "CDI",
      requirements: ["React", "TypeScript", "5+ ans"],
    },
    {
      id: 2,
      title: "Ingénieur Python",
      company: "DataFlow",
      location: "Lyon",
      type: "CDI",
      requirements: ["Python", "Django", "3+ ans"],
    },
    {
      id: 3,
      title: "Data Scientist",
      company: "AI Solutions",
      location: "Remote",
      type: "CDI",
      requirements: ["Python", "ML", "PhD"],
    },
    {
      id: 4,
      title: "DevOps Lead",
      company: "CloudTech",
      location: "Toulouse",
      type: "CDI",
      requirements: ["Kubernetes", "AWS", "Leadership"],
    },
  ]

  const matchingHistory: MatchingResult[] = [
    {
      id: 1,
      candidateName: "Ahmed Benali",
      jobTitle: "Développeur React Senior",
      score: 92,
      date: "2024-01-15",
      status: "completed",
    },
    {
      id: 2,
      candidateName: "Yasmine El Amrani",
      jobTitle: "Ingénieur Python",
      score: 88,
      date: "2024-01-14",
      status: "completed",
    },
    {
      id: 3,
      candidateName: "Sophie Laurent",
      jobTitle: "Data Scientist",
      score: 95,
      date: "2024-01-13",
      status: "completed",
    },
    {
      id: 4,
      candidateName: "Pierre Moreau",
      jobTitle: "DevOps Lead",
      score: 90,
      date: "2024-01-12",
      status: "completed",
    },
  ]

  const handleStartMatching = () => {
    setIsMatching(true)
    // Simulation du matching
    setTimeout(() => {
      setIsMatching(false)
      alert("Matching terminé ! Consultez l'historique pour voir les résultats.")
    }, 3000)
  }

  const toggleCandidateSelection = (candidateId: number) => {
    setSelectedCandidates((prev) =>
      prev.includes(candidateId) ? prev.filter((id) => id !== candidateId) : [...prev, candidateId],
    )
  }

  const toggleGroupSelection = (groupId: number) => {
    setSelectedGroups((prev) => (prev.includes(groupId) ? prev.filter((id) => id !== groupId) : [...prev, groupId]))
  }

  const toggleJobSelection = (jobId: number) => {
    setSelectedJobs((prev) => (prev.includes(jobId) ? prev.filter((id) => id !== jobId) : [...prev, jobId]))
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600"
    if (score >= 75) return "text-blue-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 90) return "default"
    if (score >= 75) return "secondary"
    return "outline"
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Matching IA</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Associez automatiquement les candidats aux offres d'emploi
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              onClick={handleStartMatching}
              disabled={
                isMatching ||
                (selectedCandidates.length === 0 && selectedGroups.length === 0) ||
                selectedJobs.length === 0
              }
              className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              {isMatching ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                  Matching en cours...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Lancer le Matching
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg dark:bg-blue-900">
                  <Users className="h-6 w-6 text-blue-600 dark:text-blue-300" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Candidats sélectionnés</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {selectedTab === "candidates"
                      ? selectedCandidates.length
                      : selectedGroups.reduce((acc, groupId) => {
                          const group = candidateGroups.find((g) => g.id === groupId)
                          return acc + (group?.count || 0)
                        }, 0)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg dark:bg-green-900">
                  <Briefcase className="h-6 w-6 text-green-600 dark:text-green-300" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Jobs sélectionnés</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{selectedJobs.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg dark:bg-purple-900">
                  <TrendingUp className="h-6 w-6 text-purple-600 dark:text-purple-300" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Score moyen</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">87%</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-orange-100 rounded-lg dark:bg-orange-900">
                  <History className="h-6 w-6 text-orange-600 dark:text-orange-300" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Matchings aujourd'hui</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">12</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Selection des Candidats */}
          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-gray-900 dark:text-white">
                <Users className="h-5 w-5" />
                Sélection des Candidats
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs value={selectedTab} onValueChange={(value: any) => setSelectedTab(value)} className={undefined}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="candidates" className={undefined}>Candidats individuels</TabsTrigger>
                  <TabsTrigger value="groups" className={undefined}>Groupes</TabsTrigger>
                </TabsList>

                <TabsContent value="candidates" className="space-y-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="Rechercher un candidat..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {candidates
                      .filter(
                        (candidate) =>
                          candidate.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          candidate.title.toLowerCase().includes(searchTerm.toLowerCase()),
                      )
                      .map((candidate) => (
                        <div
                          key={candidate.id}
                          className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                            selectedCandidates.includes(candidate.id)
                              ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                              : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                          }`}
                          onClick={() => toggleCandidateSelection(candidate.id)}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-white">{candidate.name}</h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400">{candidate.title}</p>
                              <div className="flex gap-1 mt-1">
                                {candidate.skills.slice(0, 3).map((skill) => (
                                  <Badge key={skill} variant="outline" className="text-xs">
                                    {skill}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-sm text-gray-600 dark:text-gray-400">{candidate.experience}</p>
                              <p className="text-xs text-gray-500">{candidate.location}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </TabsContent>

                <TabsContent value="groups" className="space-y-4">
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {candidateGroups.map((group) => (
                      <div
                        key={group.id}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedGroups.includes(group.id)
                            ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                            : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                        }`}
                        onClick={() => toggleGroupSelection(group.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div
                              className="w-4 h-4 rounded-full"
                              style={{
                                backgroundColor:
                                  group.color === "blue"
                                    ? "#3b82f6"
                                    : group.color === "green"
                                      ? "#10b981"
                                      : group.color === "purple"
                                        ? "#8b5cf6"
                                        : "#f59e0b",
                              }}
                            />
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-white">{group.name}</h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400">{group.count} candidats</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Selection des Jobs */}
          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-gray-900 dark:text-white">
                <Briefcase className="h-5 w-5" />
                Sélection des Offres d'Emploi
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input placeholder="Rechercher une offre..." className="pl-10" />
                </div>

                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {jobs.map((job) => (
                    <div
                      key={job.id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedJobs.includes(job.id)
                          ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                          : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                      }`}
                      onClick={() => toggleJobSelection(job.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white">{job.title}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1">
                            <Building className="h-3 w-3" />
                            {job.company}
                          </p>
                          <div className="flex gap-1 mt-1">
                            {job.requirements.slice(0, 3).map((req) => (
                              <Badge key={req} variant="outline" className="text-xs">
                                {req}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant="secondary">{job.type}</Badge>
                          <p className="text-xs text-gray-500 mt-1">{job.location}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Historique des Résultats */}
        <Card className="dark:bg-gray-800 dark:border-gray-700">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-gray-900 dark:text-white">
              <History className="h-5 w-5" />
              Historique des Matchings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-4 items-center">
                <Select defaultValue="all">
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Filtrer par statut" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tous les statuts</SelectItem>
                    <SelectItem value="completed">Terminé</SelectItem>
                    <SelectItem value="pending">En cours</SelectItem>
                    <SelectItem value="failed">Échoué</SelectItem>
                  </SelectContent>
                </Select>

                <Select defaultValue="recent">
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Période" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="recent">7 derniers jours</SelectItem>
                    <SelectItem value="month">Ce mois</SelectItem>
                    <SelectItem value="quarter">Ce trimestre</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                {matchingHistory.map((result) => (
                  <div
                    key={result.id}
                    className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-gray-500" />
                          <span className="font-medium text-gray-900 dark:text-white">{result.candidateName}</span>
                        </div>
                        <div className="text-gray-400">→</div>
                        <div className="flex items-center gap-2">
                          <Briefcase className="h-4 w-4 text-gray-500" />
                          <span className="text-gray-700 dark:text-gray-300">{result.jobTitle}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <Star className="h-4 w-4 text-yellow-500" />
                          <span className={`font-bold ${getScoreColor(result.score)}`}>{result.score}%</span>
                        </div>
                        <Badge variant={getScoreBadgeVariant(result.score)}>
                          {result.status === "completed"
                            ? "Terminé"
                            : result.status === "pending"
                              ? "En cours"
                              : "Échoué"}
                        </Badge>
                        <div className="flex items-center gap-1 text-sm text-gray-500">
                          <Calendar className="h-3 w-3" />
                          {new Date(result.date).toLocaleDateString("fr-FR")}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}

export default MatchingPage
