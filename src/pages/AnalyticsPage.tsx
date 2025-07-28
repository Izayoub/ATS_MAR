"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import Header from "../components/Layout/Header"
import Sidebar from "../components/Layout/Sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import {
  BarChart3,
  TrendingUp,
  Users,
  Briefcase,
  Clock,
  Target,
  Brain,
  Download,
  Filter,
  ArrowUp,
  ArrowDown,
  Eye,
} from "lucide-react"

const AnalyticsPage: React.FC = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState("30d")

  useEffect(() => {
    // Simulate data loading
    const timer = setTimeout(() => setLoading(false), 1000)
    return () => clearTimeout(timer)
  }, [])

  const kpis = [
    {
      title: "Candidatures Totales",
      value: "1,247",
      change: "+12.5%",
      trend: "up",
      icon: Users,
      color: "bg-blue-500",
      description: "vs mois dernier",
    },
    {
      title: "Taux de Conversion",
      value: "18.3%",
      change: "+2.1%",
      trend: "up",
      icon: Target,
      color: "bg-green-500",
      description: "candidatures → entretiens",
    },
    {
      title: "Temps Moyen de Recrutement",
      value: "12 jours",
      change: "-2 jours",
      trend: "up",
      icon: Clock,
      color: "bg-orange-500",
      description: "vs mois dernier",
    },
    {
      title: "Score IA Moyen",
      value: "87%",
      change: "+3.2%",
      trend: "up",
      icon: Brain,
      color: "bg-purple-500",
      description: "précision matching",
    },
    {
      title: "Offres Actives",
      value: "23",
      change: "+5",
      trend: "up",
      icon: Briefcase,
      color: "bg-indigo-500",
      description: "ce mois",
    },
    {
      title: "Taux de Satisfaction",
      value: "94%",
      change: "+1.8%",
      trend: "up",
      icon: TrendingUp,
      color: "bg-pink-500",
      description: "feedback candidats",
    },
  ]

  const topJobs = [
    {
      title: "Développeur Full Stack React/Node.js",
      applications: 156,
      views: 1240,
      conversionRate: 12.6,
      status: "active",
    },
    {
      title: "Data Scientist",
      applications: 89,
      views: 890,
      conversionRate: 10.0,
      status: "active",
    },
    {
      title: "Chef de Projet Digital",
      applications: 67,
      views: 567,
      conversionRate: 11.8,
      status: "active",
    },
    {
      title: "UX/UI Designer",
      applications: 45,
      views: 445,
      conversionRate: 10.1,
      status: "paused",
    },
  ]

  const sourceAnalytics = [
    { source: "ReKrute", applications: 456, percentage: 36.6, cost: 2.3 },
    { source: "Amaljob", applications: 312, percentage: 25.0, cost: 1.8 },
    { source: "LinkedIn", applications: 234, percentage: 18.8, cost: 4.2 },
    { source: "Site Web", applications: 156, percentage: 12.5, cost: 0.0 },
    { source: "Cooptation", applications: 89, percentage: 7.1, cost: 0.5 },
  ]

  const timeToHireData = [
    { stage: "Publication → Première candidature", days: 2, target: 3 },
    { stage: "Candidature → Premier tri", days: 1, target: 1 },
    { stage: "Tri → Entretien RH", days: 3, target: 5 },
    { stage: "Entretien RH → Entretien technique", days: 4, target: 7 },
    { stage: "Entretien technique → Décision", days: 2, target: 3 },
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
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Analytics RH</h1>
                <p className="text-gray-600 dark:text-gray-400">
                  Insights et métriques de performance de votre recrutement
                </p>
              </div>
              <div className="flex space-x-3">
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="7d">7 derniers jours</option>
                  <option value="30d">30 derniers jours</option>
                  <option value="90d">90 derniers jours</option>
                  <option value="1y">1 an</option>
                </select>
                <Button variant="outline">
                  <Filter className="w-4 h-4 mr-2" />
                  Filtres
                </Button>
                <Button>
                  <Download className="w-4 h-4 mr-2" />
                  Exporter
                </Button>
              </div>
            </div>

            {/* KPIs Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {kpis.map((kpi) => (
                <Card
                  key={kpi.title}
                  className="hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700"
                >
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-12 h-12 ${kpi.color} rounded-lg flex items-center justify-center`}>
                        <kpi.icon className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex items-center text-sm">
                        {kpi.trend === "up" ? (
                          <ArrowUp className="w-4 h-4 text-green-500 mr-1" />
                        ) : (
                          <ArrowDown className="w-4 h-4 text-red-500 mr-1" />
                        )}
                        <span className={kpi.trend === "up" ? "text-green-600" : "text-red-600"}>{kpi.change}</span>
                      </div>
                    </div>
                    <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-1">{kpi.value}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{kpi.title}</p>
                    <p className="text-xs text-gray-500 mt-1">{kpi.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Charts Row */}
            <div className="grid lg:grid-cols-2 gap-6 mb-8">
              {/* Applications Chart */}
              <Card className="hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 className="w-5 h-5 mr-2" />
                    Évolution des Candidatures
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="text-center">
                      <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500">Graphique des candidatures</p>
                      <p className="text-sm text-gray-400">Données des 30 derniers jours</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Conversion Funnel */}
              <Card className="hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Target className="w-5 h-5 mr-2" />
                    Entonnoir de Conversion
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      { stage: "Candidatures", count: 1247, percentage: 100 },
                      { stage: "Présélection", count: 456, percentage: 36.6 },
                      { stage: "Entretien RH", count: 234, percentage: 18.8 },
                      { stage: "Entretien technique", count: 89, percentage: 7.1 },
                      { stage: "Offre", count: 23, percentage: 1.8 },
                      { stage: "Embauche", count: 18, percentage: 1.4 },
                    ].map((item) => (
                      <div key={item.stage} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                          <span className="text-sm font-medium text-gray-900 dark:text-white">{item.stage}</span>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-purple-500 h-2 rounded-full"
                              style={{ width: `${item.percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600 dark:text-gray-400 w-12 text-right">{item.count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Performance Tables */}
            <div className="grid lg:grid-cols-2 gap-6 mb-8">
              {/* Top Performing Jobs */}
              <Card className="hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700">
                <CardHeader>
                  <CardTitle>Offres les Plus Performantes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {topJobs.map((job) => (
                      <div
                        key={job.title}
                        className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                      >
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 dark:text-white text-sm mb-1">{job.title}</h4>
                          <div className="flex items-center space-x-4 text-xs text-gray-600 dark:text-gray-400">
                            <div className="flex items-center">
                              <Users className="w-3 h-3 mr-1" />
                              {job.applications} candidatures
                            </div>
                            <div className="flex items-center">
                              <Eye className="w-3 h-3 mr-1" />
                              {job.views} vues
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-gray-900 dark:text-white">
                            {job.conversionRate}%
                          </div>
                          <div className="text-xs text-gray-500">conversion</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Source Analytics */}
              <Card className="hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700">
                <CardHeader>
                  <CardTitle>Performance par Source</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {sourceAnalytics.map((source) => (
                      <div key={source.source} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                          <span className="text-sm font-medium text-gray-900 dark:text-white">{source.source}</span>
                        </div>
                        <div className="flex items-center space-x-4">
                          <div className="text-right">
                            <div className="text-sm font-semibold text-gray-900 dark:text-white">
                              {source.applications}
                            </div>
                            <div className="text-xs text-gray-500">{source.percentage}%</div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm text-gray-600 dark:text-gray-400">{source.cost.toFixed(1)} MAD</div>
                            <div className="text-xs text-gray-500">coût/candidature</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Time to Hire Analysis */}
            <Card className="mb-8 hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="w-5 h-5 mr-2" />
                  Analyse du Temps de Recrutement
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {timeToHireData.map((item) => (
                    <div
                      key={item.stage}
                      className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
                    >
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 dark:text-white mb-1">{item.stage}</h4>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${item.days <= item.target ? "bg-green-500" : "bg-red-500"}`}
                            style={{ width: `${Math.min((item.days / item.target) * 100, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="ml-4 text-right">
                        <div
                          className={`text-lg font-bold ${
                            item.days <= item.target ? "text-green-600" : "text-red-600"
                          }`}
                        >
                          {item.days}j
                        </div>
                        <div className="text-sm text-gray-500">/ {item.target}j cible</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* AI Insights */}
            <Card className="hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Brain className="w-5 h-5 mr-2" />
                  Insights IA
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                      <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">🎯 Recommandation du jour</h4>
                      <p className="text-blue-800 dark:text-blue-200 text-sm">
                        Vos offres "Développeur React" attirent 40% plus de candidats qualifiés le mardi. Planifiez vos
                        publications en conséquence.
                      </p>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                      <h4 className="font-semibold text-green-900 dark:text-green-100 mb-2">📈 Tendance détectée</h4>
                      <p className="text-green-800 dark:text-green-200 text-sm">
                        Les candidats avec certification AWS ont un taux d'acceptation d'offre 25% plus élevé.
                      </p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="p-4 bg-purple-50 dark:bg-purple-900 rounded-lg">
                      <h4 className="font-semibold text-purple-900 dark:text-purple-100 mb-2">🔍 Analyse prédictive</h4>
                      <p className="text-purple-800 dark:text-purple-200 text-sm">
                        Basé sur les tendances actuelles, vous devriez recevoir ~45 nouvelles candidatures cette
                        semaine.
                      </p>
                    </div>
                    <div className="p-4 bg-orange-50 dark:bg-orange-900 rounded-lg">
                      <h4 className="font-semibold text-orange-900 dark:text-orange-100 mb-2">
                        ⚡ Optimisation suggérée
                      </h4>
                      <p className="text-orange-800 dark:text-orange-200 text-sm">
                        Réduisez le délai de réponse initial de 24h à 12h pour améliorer le taux de conversion de 15%.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}

export default AnalyticsPage
