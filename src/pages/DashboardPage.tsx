"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import { useNavigate } from "react-router-dom"
import { Users, Briefcase, Clock, Brain, Target, Calendar, BarChart3, ArrowUp, ArrowDown, Plus } from "lucide-react"

interface DashboardStats {
  totalCandidates: number
  activeJobs: number
  matchingAccuracy: number
  timeToHire: number
  candidatesThisMonth: number
  jobsThisMonth: number
  accuracyChange: number
  timeChange: number
}

interface RecentActivity {
  id: string
  type: "candidate" | "job" | "interview" | "match"
  title: string
  description: string
  time: string
  status: "success" | "pending" | "warning"
}

const DashboardPage: React.FC = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats>({
    totalCandidates: 0,
    activeJobs: 0,
    matchingAccuracy: 0,
    timeToHire: 0,
    candidatesThisMonth: 0,
    jobsThisMonth: 0,
    accuracyChange: 0,
    timeChange: 0,
  })
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true)
      await new Promise((resolve) => setTimeout(resolve, 1000))

      setStats({
        totalCandidates: 1247,
        activeJobs: 23,
        matchingAccuracy: 94,
        timeToHire: 12,
        candidatesThisMonth: 156,
        jobsThisMonth: 8,
        accuracyChange: 2.5,
        timeChange: -1.2,
      })

      setRecentActivity([
        {
          id: "1",
          type: "match",
          title: "Nouveau match trouvé",
          description: "Sarah Alami correspond à 96% au poste de Développeur React",
          time: "Il y a 5 minutes",
          status: "success",
        },
        {
          id: "2",
          type: "candidate",
          title: "Nouveau candidat",
          description: "Ahmed Benali a postulé pour le poste de Data Scientist",
          time: "Il y a 15 minutes",
          status: "pending",
        },
        {
          id: "3",
          type: "interview",
          title: "Entretien programmé",
          description: "Entretien avec Fatima El Mansouri prévu demain à 14h",
          time: "Il y a 1 heure",
          status: "success",
        },
        {
          id: "4",
          type: "job",
          title: "Offre publiée",
          description: "Poste de Chef de Projet publié sur ReKrute et Amaljob",
          time: "Il y a 2 heures",
          status: "success",
        },
      ])

      setLoading(false)
    }

    fetchDashboardData()
  }, [])

  const statCards = [
    {
      title: "Total Candidats",
      value: stats.totalCandidates.toLocaleString(),
      change: `+${stats.candidatesThisMonth}`,
      changeLabel: "ce mois",
      icon: Users,
      color: "bg-blue-500",
      trend: "up",
    },
    {
      title: "Offres Actives",
      value: stats.activeJobs.toString(),
      change: `+${stats.jobsThisMonth}`,
      changeLabel: "ce mois",
      icon: Briefcase,
      color: "bg-green-500",
      trend: "up",
    },
    {
      title: "Précision IA",
      value: `${stats.matchingAccuracy}%`,
      change: `+${stats.accuracyChange}%`,
      changeLabel: "vs mois dernier",
      icon: Brain,
      color: "bg-purple-500",
      trend: "up",
    },
    {
      title: "Temps de Recrutement",
      value: `${stats.timeToHire}j`,
      change: `${stats.timeChange}j`,
      changeLabel: "vs mois dernier",
      icon: Clock,
      color: "bg-orange-500",
      trend: "down",
    },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Bonjour, {user?.username} 👋</h1>
        <p className="text-gray-600 dark:text-gray-400">Voici un aperçu de votre activité de recrutement</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card) => (
          <div
            key={card.title}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 ${card.color} rounded-lg flex items-center justify-center`}>
                <card.icon className="w-6 h-6 text-white" />
              </div>
              <div
                className={`flex items-center text-sm ${card.trend === "up" ? "text-green-600" : "text-red-600"}`}
              >
                {card.trend === "up" ? (
                  <ArrowUp className="w-4 h-4 mr-1" />
                ) : (
                  <ArrowDown className="w-4 h-4 mr-1" />
                )}
                {card.change}
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{card.value}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{card.title}</p>
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{card.changeLabel}</p>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Activité Récente</h2>
              <button className="text-purple-600 hover:text-purple-700 text-sm font-medium">Voir tout</button>
            </div>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      activity.status === "success"
                        ? "bg-green-100 dark:bg-green-900"
                        : activity.status === "pending"
                          ? "bg-yellow-100 dark:bg-yellow-900"
                          : "bg-red-100 dark:bg-red-900"
                    }`}
                  >
                    {activity.type === "match" && (
                      <Target className="w-4 h-4 text-green-600 dark:text-green-400" />
                    )}
                    {activity.type === "candidate" && (
                      <Users className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                    )}
                    {activity.type === "interview" && (
                      <Calendar className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                    )}
                    {activity.type === "job" && (
                      <Briefcase className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white">{activity.title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{activity.description}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions & AI Insights */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Actions Rapides</h2>
            <div className="space-y-3">
              <button
                className="w-full flex items-center justify-center px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                onClick={() => navigate("/jobs/create")}
              >
                <Plus className="w-4 h-4 mr-2" />
                Nouvelle Offre
              </button>
              <button className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <Users className="w-4 h-4 mr-2" />
                Importer CVs
              </button>
              <button className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <BarChart3 className="w-4 h-4 mr-2" />
                Rapport IA
              </button>
            </div>
          </div>

          {/* AI Insights */}
          <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900 dark:to-blue-900 rounded-xl p-6 border border-purple-200 dark:border-purple-700">
            <div className="flex items-center mb-4">
              <Brain className="w-6 h-6 text-purple-600 dark:text-purple-400 mr-2" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Insights IA</h2>
            </div>
            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Recommandation du jour</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  3 candidats avec un score de matching &gt; 90% attendent votre attention pour le poste de
                  "Développeur Full Stack".
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Tendance détectée</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Les candidats avec des compétences en React sont 40% plus susceptibles d'accepter vos offres.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Chart */}
      <div className="mt-8">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Performance de Recrutement</h2>
            <div className="flex space-x-2">
              <button className="px-3 py-1 text-sm bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-lg">
                7 jours
              </button>
              <button className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                30 jours
              </button>
              <button className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                90 jours
              </button>
            </div>
          </div>
          <div className="h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500 dark:text-gray-400">Graphique de performance</p>
              <p className="text-sm text-gray-400 dark:text-gray-500">Les données seront affichées ici</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
