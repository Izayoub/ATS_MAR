"use client"

import { useState, useEffect } from "react"
import candidateGroupService from "../services/candidateGroupService"
import type { 
  CandidateGroup, 
  CandidateGroupCreate, 
  CandidateGroupFilters,
  GroupAnalytics,
  BulkActionRequest 
} from "../types/api"

export const useCandidateGroups = (filters?: CandidateGroupFilters) => {
  const [groups, setGroups] = useState<CandidateGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalCount, setTotalCount] = useState(0)

  const fetchGroups = async (newFilters?: CandidateGroupFilters) => {
    try {
      setLoading(true)
      setError(null)
      const response = await candidateGroupService.getGroups(newFilters || filters)
      setGroups(response.results)
      setTotalCount(response.count)
    } catch (err: any) {
      setError(err.message || "Erreur lors du chargement des groupes")
    } finally {
      setLoading(false)
    }
  }

  const createGroup = async (data: CandidateGroupCreate): Promise<CandidateGroup> => {
    try {
      const newGroup = await candidateGroupService.createGroup(data)
      setGroups(prev => [...prev, newGroup])
      setTotalCount(prev => prev + 1)
      return newGroup
    } catch (err: any) {
      throw new Error(err.message || "Erreur lors de la création du groupe")
    }
  }

  const updateGroup = async (id: number, data: Partial<CandidateGroupCreate>): Promise<CandidateGroup> => {
    try {
      const updatedGroup = await candidateGroupService.updateGroup(id, data)
      setGroups(prev => prev.map(group => group.id === id ? updatedGroup : group))
      return updatedGroup
    } catch (err: any) {
      throw new Error(err.message || "Erreur lors de la mise à jour du groupe")
    }
  }

  const deleteGroup = async (id: number): Promise<void> => {
    try {
      await candidateGroupService.deleteGroup(id)
      setGroups(prev => prev.filter(group => group.id !== id))
      setTotalCount(prev => prev - 1)
    } catch (err: any) {
      throw new Error(err.message || "Erreur lors de la suppression du groupe")
    }
  }

  const addCandidatesToGroup = async (groupId: number, candidateIds: number[]) => {
    try {
      const result = await candidateGroupService.addCandidatesToGroup(groupId, candidateIds)
      
      // Mettre à jour le compteur local
      setGroups(prev => prev.map(group => 
        group.id === groupId 
          ? { ...group, candidats_count: result.total_candidats }
          : group
      ))
      
      return result
    } catch (err: any) {
      throw new Error(err.message || "Erreur lors de l'ajout des candidats au groupe")
    }
  }

  const removeCandidatesFromGroup = async (groupId: number, candidateIds: number[]) => {
    try {
      const result = await candidateGroupService.removeCandidatesFromGroup(groupId, candidateIds)
      
      // Mettre à jour le compteur local
      setGroups(prev => prev.map(group => 
        group.id === groupId 
          ? { ...group, candidats_count: result.total_candidats }
          : group
      ))
      
      return result
    } catch (err: any) {
      throw new Error(err.message || "Erreur lors de la suppression des candidats du groupe")
    }
  }

  const bulkActions = async (request: BulkActionRequest) => {
    try {
      const result = await candidateGroupService.bulkActions(request)
      
      // Recharger les groupes après une action en lot
      if (result.success) {
        await fetchGroups()
      }
      
      return result
    } catch (err: any) {
      throw new Error(err.message || "Erreur lors de l'action en lot")
    }
  }

  useEffect(() => {
    fetchGroups()
  }, [])

  const refetch = (newFilters?: CandidateGroupFilters) => {
    fetchGroups(newFilters)
  }

  return {
    groups,
    loading,
    error,
    totalCount,
    createGroup,
    updateGroup,
    deleteGroup,
    addCandidatesToGroup,
    removeCandidatesFromGroup,
    bulkActions,
    refetch
  }
}

export const useCandidateGroupsSummary = () => {
  const [groups, setGroups] = useState<CandidateGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchGroupsSummary = async () => {
    try {
      setLoading(true)
      setError(null)
      const groupsData = await candidateGroupService.getGroupsSummary()
      setGroups(groupsData)
    } catch (err: any) {
      setError(err.message || "Erreur lors du chargement des groupes")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGroupsSummary()
  }, [])

  return {
    groups,
    loading,
    error,
    refetch: fetchGroupsSummary
  }
}

export const useCandidateGroupAnalytics = (groupId?: number) => {
  const [analytics, setAnalytics] = useState<GroupAnalytics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAnalytics = async (id?: number) => {
    const targetId = id || groupId
    if (!targetId) return

    try {
      setLoading(true)
      setError(null)
      const response = await candidateGroupService.getGroupAnalytics(targetId)
      setAnalytics(response.analytics)
    } catch (err: any) {
      setError(err.message || "Erreur lors du chargement des analytics")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (groupId) {
      fetchAnalytics()
    }
  }, [groupId])

  return {
    analytics,
    loading,
    error,
    fetchAnalytics
  }
}