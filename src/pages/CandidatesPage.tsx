"use client"

import { Button } from "../components/ui/button"
import MatchingModal from "../components/MatchingModal"

import { CandidateCard } from "../components/candidates/CandidateCard"
import { CVUploadDropzone } from "../components/CVUploadDropzone"
import { PendingCVsList } from "../components/candidates/PendingCVsList"
import { ExtractDataButton } from "../components/ExtractDataButton"
import Layout from "../components/Layout/Layout"

import type React from "react"
import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useToast } from "../contexts/ToastContext"
import { useCandidates } from "../hooks/useCandidates"
import { usePendingCandidates } from "../hooks/usePendingCandidates"
import { useCandidateGroupsSummary, useCandidateGroups } from "../hooks/useCandidateGroups"
import candidateGroupService from "../services/candidateGroupService"
import candidateService from "../services/candidateService"
import type { Candidate, CandidateFilters, CandidateGroup, CandidateGroupCreate } from "../types/api"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Users, FileText, Trash2, Upload, FolderOpen, Search, Settings, Plus, MoreVertical, Edit } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../components/ui/dropdown-menu"
import { Input } from "../components/ui/input"
import { Label } from "../components/ui/label"
import { Badge } from "../components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select"
import { CVUploadModal } from "../components/CVUploadModal"

const CandidatesPage: React.FC = () => {
  const [filters, setFilters] = useState<CandidateFilters>({
    experience_level: undefined,
    location: "",
    skills: [],
  })
  const [searchTerm, setSearchTerm] = useState("")
  const [experienceLevel, setExperienceLevel] = useState("")
  const [location, setLocation] = useState("")
  const [skills, setSkills] = useState("")

  const [showMatchingModal, setShowMatchingModal] = useState(false)
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null)
  const [showUploadModal, setShowUploadModal] = useState(false)

  const [selectedGroupId, setSelectedGroupId] = useState<string>("")
  const [showGroupModal, setShowGroupModal] = useState(false)
  const [showMultiUploadModal, setShowMultiUploadModal] = useState(false)
  const [showPendingCVs, setShowPendingCVs] = useState(false)
  const [selectedDestinationGroup, setSelectedDestinationGroup] = useState<string>("none")
  const [selectedGroup, setSelectedGroup] = useState<CandidateGroup | null>(null)
  const [showEditGroupModal, setShowEditGroupModal] = useState(false)

  // État pour la création de groupe
  const [newGroup, setNewGroup] = useState<CandidateGroupCreate>({
    nom: "",
    description: "",
    type_groupe: "custom",
    couleur: "blue",
    ordre_affichage: 0,
    is_active: true,
    is_public: false,
  })

  // Hooks pour les données
  const { candidates, loading, error, pagination, refetch } = useCandidates(filters)
  const { groups: groupsSummary, loading: groupsLoading, refetch: refetchGroups } = useCandidateGroupsSummary()
  const { createGroup, updateGroup, deleteGroup, addCandidatesToGroup } = useCandidateGroups()
  const { pendingCandidates, loading: pendingLoading } = usePendingCandidates()
  const { addToast } = useToast()
  const navigate = useNavigate()

  // Filtrer par groupe si sélectionné
  useEffect(() => {
    if (selectedGroupId && selectedGroupId !== "") {
      const newFilters = { ...filters, group: selectedGroupId, page: 1 }
      setFilters(newFilters)
      refetch(newFilters)
    } else {
      const newFilters = { ...filters }
      delete newFilters.group
      setFilters(newFilters)
      refetch(newFilters)
    }
  }, [selectedGroupId])

  const handleSearch = (term: string) => {
    setSearchTerm(term)
    const newFilters = { ...filters, search: term, page: 1 }
    setFilters(newFilters)
    refetch(newFilters)
  }

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value || undefined, page: 1 }
    setFilters(newFilters)
    refetch(newFilters)

    // Update local state
    if (key === "experience_level") setExperienceLevel(value)
    if (key === "location") setLocation(value)
    if (key === "skills") setSkills(value)
  }

  const handleDeleteCandidate = async (candidateId: number) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer ce candidat ?")) {
      try {
        await candidateService.deleteCandidate(candidateId)
        addToast("Candidat supprimé avec succès", "success")
        refetch()
      } catch (error: any) {
        addToast(error.message, "error")
      }
    }
  }

  const handleStartMatching = (candidate: Candidate) => {
    setSelectedCandidate(candidate)
    setShowMatchingModal(true)
  }

  const handleMatchingSuccess = () => {
    addToast(`Matching terminé pour ${selectedCandidate?.full_name}`, "success")
    refetch()
    setShowMatchingModal(false)
    setSelectedCandidate(null)
  }

  const handleUploadSuccess = (candidate: any) => {
    addToast(`CV importé avec succès pour ${candidate.full_name}`, "success")
    refetch()
    setShowUploadModal(false)
  }

  const handleCreateGroup = async () => {
    if (!newGroup.nom.trim()) {
      addToast("Le nom du groupe est requis", "error")
      return
    }

    try {
      await createGroup(newGroup)
      setNewGroup({
        nom: "",
        description: "",
        type_groupe: "custom",
        couleur: "blue",
        ordre_affichage: 0,
        is_active: true,
        is_public: false,
      })
      setShowGroupModal(false)
      addToast("Groupe créé avec succès", "success")
      refetchGroups()
    } catch (error: any) {
      addToast(error.message, "error")
    }
  }

  const handleDeleteGroup = async (groupId: number) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer ce groupe ? Les candidats ne seront pas supprimés.")) {
      try {
        await deleteGroup(groupId)
        addToast("Groupe supprimé avec succès", "success")

        // Réinitialiser le filtre si le groupe supprimé était sélectionné
        if (selectedGroupId === groupId.toString()) {
          setSelectedGroupId("")
        }
        refetchGroups()
      } catch (error: any) {
        addToast(error.message, "error")
      }
    }
  }

  const handleGroupFilter = (groupId: string) => {
    setSelectedGroupId(groupId)
  }

  const handleAddCandidateToGroup = async (candidateId: number, groupId: number) => {
    try {
      const result = await addCandidatesToGroup(groupId, [candidateId])

      if (result.already_in_group.length > 0) {
        addToast("Le candidat était déjà dans ce groupe", "warning")
      } else {
        addToast(`Candidat ajouté au groupe avec succès`, "success")
      }
    } catch (error: any) {
      addToast(error.message, "error")
    }
  }

  // Nouvelle fonction pour gérer l'upload avec le composant amélioré
  const handleUploadComplete = async (results: any) => {
    if (results.success) {
      addToast("Upload terminé avec succès", "success")

      if (selectedDestinationGroup && selectedDestinationGroup !== "none") {
        try {
          let candidateIds: number[] = []

          // Handle single upload response
          if (results.candidate?.id) {
            candidateIds = [results.candidate.id]
          }
          // Handle bulk upload response
          else if (results.results && Array.isArray(results.results)) {
            candidateIds = results.results.filter((r: any) => r.candidate_id).map((r: any) => r.candidate_id)
          }

          const groupId = Number.parseInt(selectedDestinationGroup)

          if (candidateIds.length > 0) {
            const addResult = await addCandidatesToGroup(groupId, candidateIds)

            if (addResult.added_count > 0) {
              addToast(`${addResult.added_count} candidat(s) ajouté(s) au groupe`, "success")
            }

            if (addResult.already_in_group.length > 0) {
              addToast(`${addResult.already_in_group.length} candidat(s) déjà dans le groupe`, "warning")
            }
          }
        } catch (error: any) {
          console.error("Erreur lors de l'ajout au groupe:", error)
          addToast("Erreur lors de l'ajout au groupe: " + error.message, "error")
        }
      }

      setShowMultiUploadModal(false)
      setSelectedDestinationGroup("none") // Reset selection
      refetch() // Recharger la liste des candidats
    }
  }

  const handleUpdateGroup = async (data: Partial<CandidateGroupCreate>) => {
    if (!selectedGroup) return

    try {
      await updateGroup(selectedGroup.id, data)
      setShowEditGroupModal(false)
      setSelectedGroup(null)
      addToast("Groupe mis à jour avec succès", "success")
      refetchGroups()
    } catch (error: any) {
      addToast(error.message, "error")
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Gestion des Candidats</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Gérez vos candidats et lancez le matching IA</p>
          </div>
          <div className="flex items-center gap-3">
            <Button onClick={() => setShowMultiUploadModal(true)} className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              <Upload className="h-4 w-4" />
              Importer CVs
            </Button>
            <Button onClick={() => setShowGroupModal(true)} variant="outline">
              <Plus className="h-4 w-4 mr-2" />
              Nouveau Groupe
            </Button>
            <ExtractDataButton />
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
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total candidats</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{pagination.count || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg dark:bg-green-900">
                  <Users className="h-6 w-6 text-green-600 dark:text-green-300" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Candidats embauchés</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {candidates.filter((c) => c.status === "hired").length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg dark:bg-yellow-900">
                  <FileText className="h-6 w-6 text-yellow-600 dark:text-yellow-300" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Nouveaux (7j)</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {
                      candidates.filter((c) => new Date(c.created_at).getTime() > Date.now() - 7 * 24 * 60 * 60 * 1000)
                        .length
                    }
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card
            className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => setShowPendingCVs(!showPendingCVs)}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">CVs En Attente</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{pendingLoading ? "..." : pendingCandidates.length}</p>
                </div>
                <Badge variant="secondary">
                  {pendingLoading ? "..." : pendingCandidates.filter((cv) => cv.status === "failed").length} échecs
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Groups Section */}
        <Card className="dark:bg-gray-800 dark:border-gray-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <CardTitle className="flex items-center gap-2 text-gray-900 dark:text-white">
              <FolderOpen className="h-5 w-5" />
              Groupes de Candidats
            </CardTitle>
            {groupsLoading && (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent" />
            )}
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3 mb-4">
              <Button variant={selectedGroupId === "" ? "default" : "outline"} onClick={() => handleGroupFilter("")}>
                Tous ({!groupsLoading ? groupsSummary.length : "..."})
              </Button>
              {groupsSummary.map((group) => (
                <div key={group.id} className="flex items-center gap-1">
                  <Button
                    variant={selectedGroupId === group.id.toString() ? "default" : "outline"}
                    onClick={() => handleGroupFilter(group.id.toString())}
                    className="flex items-center gap-2"
                  >
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: candidateGroupService.getGroupColorValue(group.couleur) }}
                    />
                    {group.nom} ({group.candidats_count})
                  </Button>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <MoreVertical className="h-3 w-3" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem onClick={() => navigate(`/groups/${group.id}/settings`)}>
                        <Settings className="mr-2 h-4 w-4" />
                        Paramètres
                      </DropdownMenuItem>

                      <DropdownMenuItem onClick={() => navigate(`/groups/${group.id}/candidates`)}>
                        <Users className="mr-2 h-4 w-4" />
                        Gérer les candidats
                      </DropdownMenuItem>

                      <DropdownMenuItem
                        onClick={() => {
                          setSelectedGroup(group)
                          setShowEditGroupModal(true)
                        }}
                      >
                        <Edit className="mr-2 h-4 w-4" />
                        Modifier le groupe
                      </DropdownMenuItem>

                      <DropdownMenuSeparator />

                      <DropdownMenuItem onClick={() => handleDeleteGroup(group.id)} className="text-red-600">
                        <Trash2 className="mr-2 h-4 w-4" />
                        Supprimer
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Pending CVs Section */}
        <PendingCVsList isVisible={showPendingCVs} onToggleVisibility={() => setShowPendingCVs(false)} />

        {/* Search and Filters */}
        <Card className="dark:bg-gray-800 dark:border-gray-700">
          <CardContent className="p-6">
            <form
              onSubmit={(e) => {
                e.preventDefault()
                handleSearch(searchTerm)
              }}
              className="flex gap-4 mb-4"
            >
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Rechercher un candidat..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
              <Button type="submit">Rechercher</Button>
            </form>

            <div className="flex gap-4">
              <select
                value={experienceLevel}
                onChange={(e) => handleFilterChange("experience_level", e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">Tous les niveaux</option>
                <option value="junior">Junior</option>
                <option value="middle">Intermédiaire</option>
                <option value="senior">Senior</option>
              </select>

              <input
                type="text"
                placeholder="Localisation"
                value={location}
                onChange={(e) => handleFilterChange("location", e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />

              <input
                type="text"
                placeholder="Compétences"
                value={skills}
                onChange={(e) => handleFilterChange("skills", e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
          </CardContent>
        </Card>

        {/* Candidates List */}
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600"></div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-red-600 mb-4">Erreur de chargement</h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
              <Button onClick={() => refetch()}>Réessayer</Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {candidates.map((candidate) => (
              <div key={candidate.id} className="relative">
                <CandidateCard
                  candidate={candidate}
                  onStartMatching={handleStartMatching}
                  onViewDetails={(id) => navigate(`/candidates/${id}`)}
                  onDelete={handleDeleteCandidate}
                  groups={groupsSummary}
                  onAddToGroup={handleAddCandidateToGroup}
                />
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {pagination.count > 0 && (
          <div className="flex justify-center items-center gap-4 mt-8">
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

        {/* Empty State */}
        {candidates.length === 0 && !loading && (
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Aucun candidat trouvé</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {selectedGroupId
                ? "Aucun candidat dans ce groupe"
                : "Commencez par importer votre premier CV pour démarrer."}
            </p>
            <Button onClick={() => setShowMultiUploadModal(true)}>
              <Upload className="h-4 w-4 mr-2" />
              Importer le premier CV
            </Button>
          </div>
        )}

        {/* Modals */}
        <MatchingModal
          isOpen={showMatchingModal}
          onClose={() => {
            setShowMatchingModal(false)
            setSelectedCandidate(null)
          }}
          candidate={selectedCandidate}
          onSuccess={handleMatchingSuccess}
        />

        <CVUploadModal
          isOpen={showUploadModal}
          onClose={() => setShowUploadModal(false)}
          onUploadComplete={(results) => {
            if (results.success) {
              handleUploadSuccess(results.candidate)
            }
          }}
        />

        {/* Enhanced Multi Upload Modal */}
        <Dialog open={showMultiUploadModal} onOpenChange={setShowMultiUploadModal}>
          <DialogContent className="max-w-5xl w-full max-h-[90vh] overflow-y-auto">
            <DialogHeader className="pb-6">
              <DialogTitle className="text-2xl font-bold flex items-center gap-3">
                <Upload className="h-6 w-6" />
                Importer des CVs
              </DialogTitle>
              <DialogDescription>
                Uploadez un ou plusieurs CVs. Ils seront automatiquement enregistrés en attente d'extraction des données.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6">
              {/* Destination Group Selection */}
              <Card className="bg-gray-50 dark:bg-gray-800">
                <CardContent className="p-4">
                  <Label htmlFor="destination-group" className="font-semibold text-base mb-3 block">
                    <FolderOpen className="h-4 w-4 inline mr-2" />
                    Groupe de destination (optionnel)
                  </Label>
                  <Select value={selectedDestinationGroup} onValueChange={setSelectedDestinationGroup}>
                    <SelectTrigger>
                      <SelectValue placeholder="📁 Aucun groupe - Candidats généraux" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">📁 Aucun groupe - Candidats généraux</SelectItem>
                      {groupsSummary.map((group) => (
                        <SelectItem key={group.id} value={group.id.toString()}>
                          📂 {group.nom} ({group.candidats_count} candidats)
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                    Les candidats pourront être ajoutés à un groupe après extraction des données.
                  </p>
                </CardContent>
              </Card>

              {/* Upload Dropzone */}
              <CVUploadDropzone
                onUploadComplete={handleUploadComplete}
                maxFiles={20}
                destinationGroup={selectedDestinationGroup === "none" ? undefined : selectedDestinationGroup}
              />
            </div>

            <DialogFooter className="flex gap-4 pt-6 border-t">
              <Button
                variant="outline"
                onClick={() => {
                  setShowMultiUploadModal(false)
                  setSelectedDestinationGroup("none")
                }}
                size="lg"
              >
                Fermer
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Group Creation Modal */}
        <Dialog open={showGroupModal} onOpenChange={setShowGroupModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Créer un Nouveau Groupe</DialogTitle>
              <DialogDescription>Organisez vos candidats en créant des groupes personnalisés.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="group-name">Nom du groupe *</Label>
                <Input
                  id="group-name"
                  value={newGroup.nom}
                  onChange={(e) => setNewGroup({ ...newGroup, nom: e.target.value })}
                  placeholder="Ex: Développeurs Frontend"
                />
              </div>
              <div>
                <Label htmlFor="group-description">Description (optionnel)</Label>
                <Input
                  id="group-description"
                  value={newGroup.description}
                  onChange={(e) => setNewGroup({ ...newGroup, description: e.target.value })}
                  placeholder="Ex: Spécialistes React et Vue.js"
                />
              </div>
              <div>
                <Label htmlFor="group-type">Type de groupe</Label>
                <Select
                  value={newGroup.type_groupe}
                  onValueChange={(value: any) => setNewGroup({ ...newGroup, type_groupe: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="competence">Par compétence</SelectItem>
                    <SelectItem value="experience">Par expérience</SelectItem>
                    <SelectItem value="projet">Par projet</SelectItem>
                    <SelectItem value="pipeline">Pipeline de recrutement</SelectItem>
                    <SelectItem value="performance">Par performance</SelectItem>
                    <SelectItem value="geographic">Par zone géographique</SelectItem>
                    <SelectItem value="custom">Personnalisé</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="group-color">Couleur</Label>
                <Select
                  value={newGroup.couleur}
                  onValueChange={(value: any) => setNewGroup({ ...newGroup, couleur: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="blue">Bleu</SelectItem>
                    <SelectItem value="green">Vert</SelectItem>
                    <SelectItem value="red">Rouge</SelectItem>
                    <SelectItem value="yellow">Jaune</SelectItem>
                    <SelectItem value="purple">Violet</SelectItem>
                    <SelectItem value="orange">Orange</SelectItem>
                    <SelectItem value="gray">Gris</SelectItem>
                    <SelectItem value="teal">Sarcelle</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowGroupModal(false)}>
                Annuler
              </Button>
              <Button onClick={handleCreateGroup}>Créer le Groupe</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Add this modal for editing groups */}
        <Dialog open={showEditGroupModal} onOpenChange={setShowEditGroupModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Modifier le Groupe</DialogTitle>
              <DialogDescription>Modifiez les informations du groupe de candidats.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="edit-group-name">Nom du groupe *</Label>
                <Input
                  id="edit-group-name"
                  defaultValue={selectedGroup?.nom}
                  onChange={(e) => setSelectedGroup((prev) => (prev ? { ...prev, nom: e.target.value } : null))}
                />
              </div>
              <div>
                <Label htmlFor="edit-group-description">Description</Label>
                <Input
                  id="edit-group-description"
                  defaultValue={selectedGroup?.description}
                  onChange={(e) => setSelectedGroup((prev) => (prev ? { ...prev, description: e.target.value } : null))}
                />
              </div>
              <div>
                <Label htmlFor="edit-group-type">Type de groupe</Label>
                <Select
                  value={selectedGroup?.type_groupe}
                  onValueChange={(value: any) =>
                    setSelectedGroup((prev) => (prev ? { ...prev, type_groupe: value } : null))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="competence">Par compétence</SelectItem>
                    <SelectItem value="experience">Par expérience</SelectItem>
                    <SelectItem value="projet">Par projet</SelectItem>
                    <SelectItem value="pipeline">Pipeline de recrutement</SelectItem>
                    <SelectItem value="performance">Par performance</SelectItem>
                    <SelectItem value="geographic">Par zone géographique</SelectItem>
                    <SelectItem value="custom">Personnalisé</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setShowEditGroupModal(false)
                  setSelectedGroup(null)
                }}
              >
                Annuler
              </Button>
              <Button
                onClick={() => {
                  if (selectedGroup) {
                    handleUpdateGroup({
                      nom: selectedGroup.nom,
                      description: selectedGroup.description,
                      type_groupe: selectedGroup.type_groupe,
                    })
                  }
                }}
              >
                Mettre à jour
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  )
}

export default CandidatesPage
