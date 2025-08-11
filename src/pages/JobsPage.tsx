import React, { useState } from 'react'
import { Plus, Search, Filter, MapPin, Clock, Users, Eye, Edit, Trash2 } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent } from '../components/ui/card'
import { useJobs } from '../hooks/useJobs'
import type { JobFilters } from '../types/api'
import { useToast } from '../contexts/ToastContext'
import jobService from '../services/JobService'
import { useNavigate } from "react-router-dom"

const JobsPage: React.FC = () => {
  const [filters, setFilters] = useState<JobFilters>({})
  const [searchTerm, setSearchTerm] = useState('')
  const { jobs, loading, error, pagination, refetch } = useJobs(filters)
  const { addToast } = useToast()
  const navigate = useNavigate()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const newFilters = { ...filters, search: searchTerm, page: 1 }
    setFilters(newFilters)
    refetch(newFilters)
  }

  const handleFilterChange = (key: keyof JobFilters, value: string) => {
    const newFilters = { ...filters, [key]: value, page: 1 }
    setFilters(newFilters)
    refetch(newFilters)
  }

  const handleDeleteJob = async (jobId: number) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette offre ?')) {
      try {
        await jobService.deleteJob(jobId)
        addToast('Offre supprimée avec succès', 'success')
        refetch()
      } catch (error: any) {
        addToast(error.message, 'error')
      }
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
      case 'draft': return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
      case 'paused': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
      case 'closed': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
    }
  }

  const getExperienceLabel = (level: string) => {
    switch (level) {
      case 'junior': return 'Junior (0-2 ans)'
      case 'middle': return 'Confirmé (2-5 ans)'
      case 'senior': return 'Senior (5+ ans)'
      default: return level
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Erreur</h2>
          <p className="text-gray-600 dark:text-gray-400">{error}</p>
          <Button onClick={() => refetch()} className="mt-4">
            Réessayer
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Offres d'emploi
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Gérez vos offres d'emploi et suivez les candidatures
          </p>
        </div>
        <Button className="flex items-center gap-2" onClick={() => navigate("/jobs/create")}>
          <Plus className="h-4 w-4" />
          Nouvelle offre
        </Button>
      </div>

      {/* Filtres et recherche */}
      <Card>
        <CardContent className="p-6">
          <form onSubmit={handleSearch} className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Rechercher une offre..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              />
            </div>
            <Button type="submit">
              Rechercher
            </Button>
          </form>

          <div className="flex gap-4">
            <select
              value={filters.status || ''}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            >
              <option value="">Tous les statuts</option>
              <option value="active">Active</option>
              <option value="draft">Brouillon</option>
              <option value="paused">En pause</option>
              <option value="closed">Fermée</option>
            </select>

            <select
              value={filters.experience_level || ''}
              onChange={(e) => handleFilterChange('experience_level', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            >
              <option value="">Tous les niveaux</option>
              <option value="junior">Junior</option>
              <option value="middle">Confirmé</option>
              <option value="senior">Senior</option>
            </select>

            <input
              type="text"
              placeholder="Localisation"
              value={filters.location || ''}
              onChange={(e) => handleFilterChange('location', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            />
          </div>
        </CardContent>
      </Card>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Total offres */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg dark:bg-blue-900">
                <Users className="h-6 w-6 text-blue-600 dark:text-blue-300" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total des offres
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {pagination.count}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actives */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg dark:bg-green-900">
                <Clock className="h-6 w-6 text-green-600 dark:text-green-300" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Offres actives
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {jobs.filter(job => job.status === 'active').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Brouillon */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg dark:bg-yellow-900">
                <Filter className="h-6 w-6 text-yellow-600 dark:text-yellow-300" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  En brouillon
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {jobs.filter(job => job.status === 'draft').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Fermées */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg dark:bg-red-900">
                <MapPin className="h-6 w-6 text-red-600 dark:text-red-300" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Fermées
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {jobs.filter(job => job.status === 'closed').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Liste des offres */}
      <div className="grid gap-6">
        {jobs.map((job) => (
          <Card key={job.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      {job.title}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                      {job.status === 'active' ? 'Active' : 
                       job.status === 'draft' ? 'Brouillon' :
                       job.status === 'paused' ? 'En pause' : 'Fermée'}
                    </span>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                    <div className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {job.location}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {getExperienceLabel(job.experience_level)}
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4" />
                      {job.applications_count} candidature{job.applications_count !== 1 ? 's' : ''}
                    </div>
                  </div>

                  <p className="text-gray-700 dark:text-gray-300 mb-3 line-clamp-2">
                    {job.description}
                  </p>

                  <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <span>{job.company.name}</span>
                    <span>•</span>
                    <span>{job.contract_type}</span>
                    {job.salary_min && job.salary_max && (
                      <>
                        <span>•</span>
                        <span>{job.salary_min}€ - {job.salary_max}€</span>
                      </>
                    )}
                    <span>•</span>
                    <span>Créée le {new Date(job.created_at).toLocaleDateString('fr-FR')}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 ml-4">
                  <Button variant="outline" size="sm" onClick={() => navigate(`/jobs/${job.id}`)}>
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => navigate(`/jobs/${job.id}/edit`)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleDeleteJob(job.id)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Pagination */}
      {pagination.count > 0 && (
        <div className="flex justify-center items-center gap-4 mt-8">
          <Button
            variant="outline"
            disabled={!pagination.previous}
            onClick={() => {
              const newFilters = { ...filters, page: (filters.page || 1) - 1 }
              setFilters(newFilters)
              refetch(newFilters)
            }}
          >
            Précédent
          </Button>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Page {filters.page || 1}
          </span>
          <Button
            variant="outline"
            disabled={!pagination.next}
            onClick={() => {
              const newFilters = { ...filters, page: (filters.page || 1) + 1 }
              setFilters(newFilters)
              refetch(newFilters)
            }}
          >
            Suivant
          </Button>
        </div>
      )}

      {jobs.length === 0 && !loading && (
        <div className="text-center py-12">
          <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Aucune offre d'emploi
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Commencez par créer votre première offre d'emploi.
          </p>
          <Button onClick={() => navigate("/jobs/create")}>
            <Plus className="h-4 w-4 mr-2" />
            Créer une offre
          </Button>
        </div>
      )}
    </div>
  )
}

export default JobsPage
